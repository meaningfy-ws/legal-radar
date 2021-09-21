FROM cschranz/gpu-jupyter:v1.4_cuda-11.0_ubuntu-20.04

COPY requirements.txt ./requirements.txt
RUN conda install --force-reinstall -y -q -c conda-forge --file requirements.txt