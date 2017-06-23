#!/usr/bin/env python

# requires awscli: install using pip install awscli
# usage: python get_abide_fs.py /path/to/subject_file
# run from derired output directory

import os, sys, errno, subprocess

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
mkdir_p(datadir)

subjects_list = []
with open(subjfile) as subjects:
    for subject in subjects:
        subjects_list.append(subject.strip('\n'))

# get data from amazon s3
abide_url = 's3://fcp-indi/data/Projects/ABIDE_Initiative/Outputs/'
fspath = 'freesurfer/5.1/'

for subject in subjects_list:
    outdir = os.path.join(datadir, 'derivatives', 'freesurfer', subject)
    fsdir = os.path.join(abide_url, fspath, subj)
    mkdir_p(outdir)
    os.system('aws s3 cp --recursive --no-sign-request {} {}'.format(fsdir, outdir))
