FROM apache/airflow:2.2.2-python3.8

# quick sudo
USER root
RUN apt-get update && apt-get install make && apt-get install build-essential git -y

# back to normal user
USER airflow
