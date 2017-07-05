#!/usr/bin/env python

# script for adding deepqc scores to all_entries.json file for mindcontrol
# usage: python add_deepqc.py <path/to/subject_list.txt>

import os, sys, json
from nipype.utils.filemanip import save_json
os.chdir('/Users/amandae/Documents/clowd_control/pipelines/abide-fs/')

# files
subjfile = sys.argv[1]
fsfile = 'all_entries.json'
qcfile = 'qc-results.json'

# subject list
subjects_list = []
with open(subjfile) as subjects:
    for subject in subjects:
        subjects_list.append(subject.strip('\n'))

# deep qc scores
os.system('cp derivatives/qc-results.json data/derivatives/mindcontrol_freesurfer/')
os.chdir('data/derivatives/mindcontrol_freesurfer')
pwdfiles = os.listdir(os.getcwd())
if 'old_all_entries.json' not in pwdfiles:
    os.system('cp all_entries.json old_all_entries.json')

with open(qcfile) as qcfile:
    qcdata = json.load(qcfile)

qckeys = qcdata.keys()
for s in range(len(qcdata)):
    qcdata[qckeys[s][-7:]] = qcdata.pop(qckeys[s])

# add deepqc to all_entries

with open(fsfile) as fsfile:
    fsdata = json.load(fsfile)

fsdata_qc = fsdata
ne = len(fsdata) / len(subjects_list)
for entry in range(len(subjects_list)):
    new_entry = fsdata_qc[entry*ne+1]
    subjid = new_entry['subject_id'][-7:] 
    rating = qcdata[subjid]
    rating = float(rating)    
    new_entry['metrics'][u'deepqc'] = rating
    fsdata_qc[entry*ne+1] = new_entry
    
# save new output file
save_json("all_entries.json",fsdata_qc)

