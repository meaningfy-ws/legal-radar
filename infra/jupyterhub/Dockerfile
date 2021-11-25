FROM python:3.8.12

WORKDIR /app/analysis

USER root
RUN apt-get upgrade -y && apt-get update -y && apt-get install make && apt-get install build-essential git -y
RUN apt-get install npm nodejs -y && \
    npm install -g configurable-http-proxy && \
    pip3 install jupyterhub && \
    pip3 install --upgrade notebook && \
    pip3 install pandas scipy matplotlib && \
    pip3 install "dask[distributed,dataframe]" && \   
    pip3 install dask_labextension && \
    useradd admin && echo admin:change.it! | chpasswd && mkdir /home/admin && chown admin:admin /home/admin

ADD jupyterhub_config.py /app/analysis/jupyterhub_config.py
ADD create-user.py /app/analysis/create-user.py

CMD ["jupyterhub", "--ip=0.0.0.0", "--port=8887", "--no-ssl", "--allow-root"]

EXPOSE 8887
