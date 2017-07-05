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

os.system('cp all_entries.json old_all_entries.json')

with open(qcfile) as qcfile:
    qcdata = json.load(qcfile)

qcdict = []
for key, value in qcdata.iteritems():
    temp = [key,value]
    qcdict.append(temp)

qc_ratings = []
for s in range(len(qcdict)):
    temp = qcdict[s][1][0:8]
    qc_ratings.append(float(str(temp)))

# add deepqc to all_entries

with open(fsfile) as fsfile:
    fsdata = json.load(fsfile)

fsdata_qc = fsdata
temp = fsdata_qc[0]
for entry in range(len(fsdata)/3):
    new_entry = fsdata_qc[entry*3+1] 
    new_entry['metrics'][u'crocodoyle-qc'] = qc_ratings[entry]
    fsdata_qc[entry*3+1] = new_entry
    
# save new output file
save_json("all_entries.json",fsdata_qc)

