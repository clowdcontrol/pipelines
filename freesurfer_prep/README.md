# Brief instructions
## Build and run the docker container from source 
### Clone repo and cd into the directory
``` 
git clone https://github.com/clowdcontrol/pipelines/tree/master/freesurfer_prep
cd freesurfer_prep

docker build -t freesurfer_prep .

docker run -it --rm -v /path/to/bids_dir:/data clowdcontrol/freesurfer_prep
```

## ... or run directly from the [DockerHub](https://hub.docker.com/r/clowdcontrol/freesurfer_prep/) image (Current verision is v0.2)
```docker run -it --rm -v /path/to/bids_dir:/data clowdcontrol/freesurfer_prep:v0.2```
