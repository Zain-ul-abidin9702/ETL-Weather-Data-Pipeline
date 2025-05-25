FROM apache/airflow:2.9.1-python3.10
USER root
RUN apt-get update && \
    apt-get -y install git && \
    apt-get clean
USER airflow