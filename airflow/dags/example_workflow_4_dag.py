"""
# Example DAG 4

"""
import os
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.ecs_operator import ECSOperator
from datetime import datetime, timedelta

# Set up a DAG
default_args = {
    'start_date': datetime(2015, 12, 1)
}
dag = DAG(
    'Example_4',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
)
dag.doc_md = __doc__


TASK_DEF = os.environ['TASK_DEF']
TASK_SUBNET = os.environ['TASK_SUBNET']
FARGATE_CLUSTER = os.environ['FARGATE_CLUSTER']
S3_BUCKET = os.environ['S3_BUCKET']

# Setup what jobs you want to run for crunching stats
# this is just a list of tuples of the cli arguments that
# go into fargatejob/crunch_stats.py
crunch_job_configs = [
    (0, 100),
    (0, 200),
    (0, 300),
    (0, 400)
]

def construct_crunch_job_task(start_item, end_item):
    return ECSOperator(
        task_id = f'crunch_stats{start_item}_{end_item}',
        launch_type='FARGATE',
        overrides= {
        },
        network_configuration = {
            'awsvpcConfiguration': {
                'subnets': [TASK_SUBNET],
                'assignPublicIp': 'ENABLED'
            },
        },
        task_definition = TASK_DEF,
        cluster=FARGATE_CLUSTER,
        platform_version='LATEST',
        region_name='us-east-1',
        dag=dag
    )
    pass

construct_crunch_job_task(crunch_job_configs[0][0], crunch_job_configs[0][1])
