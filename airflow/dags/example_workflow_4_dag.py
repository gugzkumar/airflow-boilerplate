"""
# Example DAG 4

This Dag demonstrates how one can leverage Ariflow and AWS Fargate to perform large cost effective ETL operations. `.aws-infrastructure` is used to build the required AWS resources.


First we use `fargatejob/crunch_stats.py` to do partial computations,
and then summarize them with `fargatejob/summarize_interesting_stats.py`.
We have slack jobs to act as _notifications when tasks fail or succeed.

Example of how this would look in production:<br>
<img src="https://www.talend.com/wp-content/uploads/Picture6.png" width="600" />
<br>
^ [https://www.talend.com/blog/2019/08/01/etl-jobs-on-serverless-platforms-using-apache-airflow/](https://www.talend.com/blog/2019/08/01/etl-jobs-on-serverless-platforms-using-apache-airflow/)
"""
import os
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.ecs_operator import ECSOperator
from airflow.operators.slack_operator import SlackAPIOperator,SlackAPIPostOperator
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
SLACK_OAUTH_TOKEN = os.environ['SLACK_OAUTH_TOKEN']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

# Setup what jobs you want to run for crunching stats
# this is just a list of tuples of the cli arguments that
# go into fargatejob/crunch_stats.py
crunch_job_configs = [
    (0, 100),
    (101, 200),
    (201, 300),
    (301, 400)
]

crunch_job_tasks = []
crunch_message_job_tasks = []

def construct_crunch_job_task(start_item, end_item):
    return ECSOperator(
        task_id = f'crunch_stats_{start_item}_{end_item}',
        launch_type='FARGATE',
        overrides= {
            'containerOverrides': [
                {
                    'name': 'AirflowBoilerplateJob',
                    'command': [
                        'python',
                        'crunch_stats.py',
                        f'{start_item}',
                        f'{end_item}'
                    ],
                    'environment': [
                        {
                            'name': 'S3_BUCKET',
                            'value': S3_BUCKET
                        },
                        {
                            # TODO: Figure out how not to pass Keys
                            'name': 'AWS_ACCESS_KEY_ID',
                            'value': AWS_ACCESS_KEY_ID
                        },
                        {
                            'name': 'AWS_SECRET_ACCESS_KEY',
                            'value': AWS_SECRET_ACCESS_KEY
                        },
                    ],
                }
            ]
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


def construct_summarize_job_task():
    return ECSOperator(
        task_id = f'summarize_stats',
        launch_type='FARGATE',
        overrides= {
            'containerOverrides': [
                {
                    'name': 'AirflowBoilerplateJob',
                    'command': [
                        'python',
                        'summarize_interesting_stats.py'
                    ],
                    'environment': [
                        {
                            'name': 'S3_BUCKET',
                            'value': S3_BUCKET
                        },
                        {
                            # TODO: Figure out how not to pass Keys
                            'name': 'AWS_ACCESS_KEY_ID',
                            'value': AWS_ACCESS_KEY_ID
                        },
                        {
                            'name': 'AWS_SECRET_ACCESS_KEY',
                            'value': AWS_SECRET_ACCESS_KEY
                        },
                    ],
                }
            ]
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
        trigger_rule='all_success',
        dag=dag
    )

def construct_slack_message_task(task_id, message, trigger_rule='all_success'):
    return SlackAPIPostOperator(
        task_id=task_id,
        token = SLACK_OAUTH_TOKEN,
        channel ='#airflow-boilerplate',
        text = message,
        trigger_rule=trigger_rule,
        dag=dag
    )


# Create Crunch Job
for start_item, end_item in crunch_job_configs:
    job_task = construct_crunch_job_task(start_item, end_item)
    confirm_message_task = construct_slack_message_task(
        f'Confirm_Crunch_{start_item}_{end_item}_notification',
        f':heavy_check_mark: SUCCESS: Job to Crunch Stats for Item #{start_item} to Item #{end_item}'
    )
    fail_message_task = construct_slack_message_task(
        f'Fail_Crunch_{start_item}_{end_item}_notification',
        f':x: FAIL: Job to Crunch Stats for Item #{start_item} to Item #{end_item}',
        trigger_rule = 'all_failed'
    )
    job_task >> confirm_message_task
    job_task >> fail_message_task
    crunch_job_tasks.append(job_task)
    crunch_message_job_tasks.append(confirm_message_task)

# Create Summarize Jobs
summarize_job_task = construct_summarize_job_task()
crunch_message_job_tasks >> summarize_job_task

confirm_summarize_message_task = construct_slack_message_task(
    f'Confirm_Summarize_notification',
    f':heavy_check_mark: SUCCESS: Summarizing Stats'
)
fail_summarize_message_task = construct_slack_message_task(
    f'Fail_Summarize_notification',
    f':x: FAIL: Summarizing Stats',
    trigger_rule = 'all_failed'
)
summarize_job_task >> confirm_summarize_message_task
summarize_job_task >> fail_summarize_message_task
