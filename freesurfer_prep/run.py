import os
import os.path as op
import uuid
import shutil
from glob import glob
from nipype import MapNode, Workflow, Node
from nipype.interfaces.freesurfer import MRIConvert
from nipype.interfaces.io import DataSink
from nipype.interfaces.utility import IdentityInterface, Function
from fire import Fire

volumes = ["brainmask.mgz", "wm.mgz", "aparc+aseg.mgz", "ribbon.mgz", "T1.mgz"]

#this function finds data in the subjects_dir 
def data_grabber(subjects_dir, subject, volumes):
    import os
    volumes_list = [os.path.join(subjects_dir, subject, 'mri', volume) for volume in volumes]
    return volumes_list


#this function parses the aseg.stats, lh.aparc.stats and rh.aparc.stats and returns a dictionary
def parse_stats(subjects_dir, subject):
    from os.path import join, exists
    
    aseg_file = join(subjects_dir, subject, "stats", "aseg.stats")
    lh_aparc = join(subjects_dir, subject, "stats", "lh.aparc.stats")
    rh_aparc = join(subjects_dir, subject, "stats", "rh.aparc.stats")
    
    assert exists(aseg_file), "aseg file does not exists for %s" %subject
    assert exists(lh_aparc), "lh aparc file does not exists for %s" %subject
    assert exists(rh_aparc), "rh aparc file does not exists for %s" %subject
    
    def convert_stats_to_json(aseg_file, lh_aparc, rh_aparc):
        import pandas as pd
        import numpy as np

        def extract_other_vals_from_aseg(f):
            #line_numbers = [18,23,21,33,22]
            line_numbers = [15, 20, 22]
            output = pd.DataFrame()
            with open(f,"r") as q:
                out = q.readlines()
                for line in line_numbers:
                    sname= out[line].split(",")[1][1:]
                    vol = out[line].split(",")[-2]
                    output = output.append(pd.Series({"StructName":sname,"Volume_mm3":vol}),ignore_index=True)
            return output

        df = pd.DataFrame(np.genfromtxt(aseg_file,dtype=str),columns=["Index",
                                                            "SegId",
                                                            "NVoxels",
                                                            "Volume_mm3",
                                                            "StructName",
                                                            "normMean",
                                                            "normStdDev",
                                                            "normMin",
                                                            "normMax",
                                                            "normRange"])

        df = df.append(extract_other_vals_from_aseg(aseg_file), ignore_index=True)
        
        aparc_columns = ["StructName", "NumVert", "SurfArea", "GrayVol",
                        "ThickAvg", "ThickStd", "MeanCurv", "GausCurv",
                        "FoldInd", "CurvInd"]
        tmp_lh = pd.DataFrame(np.genfromtxt(lh_aparc,dtype=str),columns=aparc_columns)
        tmp_lh["StructName"] = "lh_"+tmp_lh["StructName"]
        tmp_rh = pd.DataFrame(np.genfromtxt(rh_aparc,dtype=str),columns=aparc_columns)
        tmp_rh["StructName"] = "rh_"+tmp_rh["StructName"]

        aseg_melt = pd.melt(df[["StructName","Volume_mm3"]], id_vars=["StructName"])
        aseg_melt.rename(columns={"StructName": "name"},inplace=True)
        aseg_melt["value"] = aseg_melt["value"].astype(float)
        
        lh_aparc_melt = pd.melt(tmp_lh,id_vars=["StructName"])
        lh_aparc_melt["value"] = lh_aparc_melt["value"].astype(float)
        lh_aparc_melt["name"] = lh_aparc_melt["StructName"]+ "_"+lh_aparc_melt["variable"]
        
        rh_aparc_melt = pd.melt(tmp_rh, id_vars=["StructName"])
        rh_aparc_melt["value"] = rh_aparc_melt["value"].astype(float)
        rh_aparc_melt["name"] = rh_aparc_melt["StructName"]+ "_"+rh_aparc_melt["variable"]
        
        output = aseg_melt[["name",
                           "value"]].append(lh_aparc_melt[["name",
                                                           "value"]],
                                            ignore_index=True).append(rh_aparc_melt[["name",
                                                                                     "value"]],
                                                                      ignore_index=True)
        outdict = output.to_dict(orient="records")
        final_dict = {}
        for pair in outdict:
           final_dict[pair["name"]] = pair["value"]
        return final_dict
    
    output_dict = convert_stats_to_json(aseg_file, lh_aparc, rh_aparc)
    return output_dict


# This function creates valid Mindcontrol entries that are saved as .json files. 
# They can be loaded into the Mindcontrol database later

def create_mindcontrol_entries(mindcontrol_base_dir, output_dir, subject, stats):
    import os
    from nipype.utils.filemanip import save_json
    
    metric_split = {"brainmask": ["ICV", "CortexVol", "TotalGrayVol"],
                    "wm": [ "Right-WM-hypointensities","Left-WM-hypointensities"],
                    "aparcaseg":[],
                    "ribbon":[]}
    volumes = ["brainmask.mgz", "wm.mgz", "aparc+aseg.mgz", "ribbon.mgz", "T1.mgz" ]
    volumes_list = [os.path.join(output_dir, subject, volume) for volume in volumes]

    all_entries = []
    
    for idx, entry_type in enumerate(["brainmask", "wm", "aparcaseg"]):
        entry = {"entry_type": entry_type, 
                 "subject_id": subject, 
                 "name": subject}
        base_img = os.path.relpath(volumes_list[-1], mindcontrol_base_dir)
        overlay_img = os.path.relpath(volumes_list[idx], mindcontrol_base_dir)
        entry["check_masks"] = [base_img, overlay_img]
        entry["metrics"] = {}
        for metric_name in metric_split[entry_type]:
            entry["metrics"][metric_name] = stats.pop(metric_name)
        if not len(metric_split[entry_type]):
            entry["metrics"] = stats
        all_entries.append(entry)
    
    output_json = os.path.abspath("mindcontrol_entries.json")
    save_json(output_json, all_entries)
    return output_json


# read in from derivatives/freesurfer/<subject_names>
# output to derivatives/freesurfer_mindcontrol/<subject_names>

def run_workflow(bids_dir):
    subjects_dir = os.path.join(bids_dir, "derivatives", "freesurfer")
    mindcontrol_base_dir = os.path.join(bids_dir, "derivatives", "mindcontrol_freesurfer")
    mindcontrol_outdir = mindcontrol_base_dir
    workflow_working_dir = os.path.join(mindcontrol_base_dir, "scratch"+"_"+str(uuid.uuid4()))

    subject_paths = glob(op.join(subjects_dir, "*"))

    subjects = []
    for path in subject_paths:
        subject = path.split('/')[-1]
        # check if mri dir exists, and don't add fsaverage
        if op.exists(op.join(path, 'mri')) and subject != 'fsaverage':
            subjects.append(subject)


    input_node = Node(IdentityInterface(fields=['subject_id',"subjects_dir",
                                            "mindcontrol_base_dir", "output_dir"]), name='inputnode')
    input_node.iterables=("subject_id", subjects)
    input_node.inputs.subjects_dir = subjects_dir
    input_node.inputs.mindcontrol_base_dir = mindcontrol_base_dir #this is where start_static_server is running
    input_node.inputs.output_dir = mindcontrol_outdir #this is in the freesurfer/ directory under the base_dir

    dg_node=Node(Function(input_names=["subjects_dir", "subject", "volumes"],
                          output_names=["volume_paths"], 
                          function=data_grabber), 
                 name="datagrab")
    #dg_node.inputs.subjects_dir = subjects_dir
    dg_node.inputs.volumes = volumes


    mriconvert_node = MapNode(MRIConvert(out_type="niigz"), 
                              iterfield=["in_file"], 
                              name='convert')

    get_stats_node = Node(Function(input_names=["subjects_dir", "subject"],
                                   output_names = ["output_dict"],
                                   function=parse_stats), name="get_freesurfer_stats")

    write_mindcontrol_entries = Node(Function(input_names = ["mindcontrol_base_dir",
                                                             "output_dir",
                                                             "subject",
                                                             "stats"],
                                              output_names=["output_json"],
                                              function=create_mindcontrol_entries), 
                                     name="get_mindcontrol_entries")

    datasink_node = Node(DataSink(),
                         name='datasink')
    subst = [('out_file',''),('_subject_id_',''),('_out','')]  + [("_convert%d" % index, "") for index in range(len(volumes))] 
    datasink_node.inputs.substitutions = subst

    wf = Workflow(name="MindPrepFS")
    wf.base_dir = workflow_working_dir
    wf.connect(input_node,"subject_id", dg_node,"subject")
    wf.connect(input_node,"subjects_dir", dg_node, "subjects_dir")
    wf.connect(input_node, "subject_id", get_stats_node, "subject")
    wf.connect(input_node, "subjects_dir", get_stats_node, "subjects_dir")
    wf.connect(input_node, "subject_id", write_mindcontrol_entries, "subject")
    wf.connect(input_node, "mindcontrol_base_dir", write_mindcontrol_entries, "mindcontrol_base_dir")
    wf.connect(input_node, "output_dir", write_mindcontrol_entries, "output_dir")
    wf.connect(get_stats_node, "output_dict", write_mindcontrol_entries, "stats")
    wf.connect(input_node, "output_dir", datasink_node, "base_directory")
    wf.connect(dg_node,"volume_paths", mriconvert_node, "in_file")
    wf.connect(mriconvert_node,'out_file',datasink_node,'out_file')
    wf.connect(write_mindcontrol_entries, "output_json", datasink_node, "out_file.@json")
    wf.run()

    shutil.rmtree(workflow_working_dir)

if __name__ == '__main__':
    Fire(run_workflow)
