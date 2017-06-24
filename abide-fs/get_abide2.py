#!/usr/bin/env python

# requires awscli: install using:
# - sudo apt-get install awscli
# - pip install awscli
# usage: python get_abide2.py /path/to/testsubjs.txt
# run from desired output directory
from __future__ import print_function

import os, sys, errno

subjfile = sys.argv[1]
mcdir = os.getcwd()

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

datadir = os.path.join(mcdir, 'data')
mkdir_p(os.path.join(datadir,'abide2_rawdata'))

subjects_list = []
sites_list = []
with open(subjfile) as subjects:
    for subject in subjects:
        subj_temp = subject.strip('\n')
        sites_list.append(subj_temp.split('\t')[0])
        subjects_list.append(subj_temp.split('\t')[1])

# get data from amazon s3
abide_url = 's3://fcp-indi/data/Projects/ABIDE2/RawData'

for s in range(len(subjects_list)):
    sitedir = 'ABIDEII-' + sites_list[s]
    sub = 'sub-' + subjects_list[s]
    s3path = os.path.join(abide_url, sitedir, sub, 'ses-1') 
    outdir = os.path.join(datadir, 'abide2_rawdata', subjects_list[s])
    os.system('aws s3 cp --recursive --no-sign-request {} {}'.format(s3path, outdir))


