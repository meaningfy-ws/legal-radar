FROM cschranz/gpu-jupyter:v1.4_cuda-11.0_ubuntu-20.04
# quick sudo
USER root
RUN apt-get update && apt-get install make && apt-get install build-essential -y
# back to normal user
USER jovyan
# working at $HOME
WORKDIR $HOME
RUN python -m pip install --upgrade pip

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
