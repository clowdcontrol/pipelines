#!/usr/bin/env python

import numpy as np

qcfile = 'bids_qc_output.txt'

subj_list = []
qc_list = []
with open(qcfile) as subjects:
    for subject in subjects:
        subj_list.append(subject[21:32])
	qc_list.append(subject[-9:-1])

qc_prob = np.zeros([len(qc_list),1])
for q in range(len(qc_prob)):
    qc_prob[q] = float(qc_list[q])


print("FAILED QC:")
for s in range(len(qc_list)):
    if qc_prob[s] < .6:		
        print('%s %f' %(subj_list[s], qc_prob[s]))

