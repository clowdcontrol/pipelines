# Brief instructions
# Clone repo and cd into the directory
``` 
git clone https://github.com/clowdcontrol/pipelines/tree/master/freesurfer_prep
cd freesurfer_prep
```
# Build docker container:
```docker build -t freesurfer_prep .```
# Run container
```docker run -it --rm -v /path/to/bids_dir:/data freesurfer_prep```
