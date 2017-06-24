FROM ubuntu:xenial
RUN apt-get update
RUN apt-get install -y python3 python3-pip git
RUN pip3 install awscli
RUN git clone https://github.com/clowdcontrol/pipelines.git /pipelines

WORKDIR /data

ENTRYPOINT ["python3", "/pipelines/abide-fs/get_abide_fs_qc.py", "/pipelines/abide_fs/test_1subj.txt", "both"]
