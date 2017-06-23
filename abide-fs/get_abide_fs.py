
# requires awscli: install using pip install awscli
# run from mindcontrol directory

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

datadir = mcdir + '/data/'
mkdir_p(datadir)

text_file = open(mcdir + '/' + subjfile, "r")
subjids = text_file.readlines()
for s in range(len(subjids)):
    temp = subjids[s]
    subjids[s] = temp[:-1]

# get data from amazon s3
abide_url = 's3://fcp-indi/data/Projects/ABIDE_Initiative/Outputs/'
fspath = 'freesurfer/5.1/'

for s in range(len(subjids)):
    outdir = datadir + subjids[s] + '/derivatives/freesurfer/'
    fsdir = abide_url + fspath + subjids[s]
    os.system('aws s3 cp --recursive --no-sign-request {} {}'.format(fsdir, outdir))
