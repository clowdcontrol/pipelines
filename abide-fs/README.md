# Brief instructions
# Clone repo and cd into the directory
``` 
git clone https://github.com/clowdcontrol/pipelines/tree/master/abide-fs
cd abide-fs
```
# Build docker container:
```
docker build -t abide-fs .
```
# Run container:
```
docker run --rm -ti -v ${PWD}:/data -v </full/path/to/subjfile.txt>:/mysubs.txt clowdcontrol/abide-fs:v0.5 /mysubs.txt <download_option>
```
download_option = bids, fs, or both (to download both bids and freesurfer)
```
```
# Subject file for QC (subjs_qc.txt):
```
10 pass, 10 fail from KKI, Stanford, UM_1
```
