# Brief instructions
# Clone repo and cd into the directory
``` 
git clone https://github.com/clowdcontrol/pipelines/tree/master/abide-fs
cd abide-fs
```
# Build docker container:
```docker build -t abide-fs .```
# Run container
```docker run -it --rm -v $PWD:/data abide-fs```
