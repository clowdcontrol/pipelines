FROM nipype/nipype:latest

RUN pip install fire
RUN git clone https://github.com/clowdcontrol/pipelines.git /pipelines

ENTRYPOINT ["python", "/pipelines/freesurfer_prep/run.py", "/data"]
