FROM apache/airflow:1.10.10-python3.7

RUN pip install boto3 --user
RUN pip install pandas --user
RUN pip install pymongo --user
RUN pip install s3fs --user
RUN pip install docker --user
RUN pip install kubernetes --user
RUN pip install websocket-client --user
RUN pip install slackclient --user

ADD ./dags /opt/airflow/dags
ADD ./plugins /opt/airflow/plugins
ADD ./startup.sh /opt/airflow/startup.sh

# ENV PYTHONUNBUFFERED 1
ENTRYPOINT []
