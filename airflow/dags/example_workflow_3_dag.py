"""
# Example DAG 3
This workflow is an example of how to leverage the KubernetesPodOperator
using airflow. For complicated sets of jobs that have their own dependencies
and what not, having work offloaded to a kubernetes cluster is effective.
<br><br>
To test this workflow you are required to have a kubernetes cluster and `config`
file used by kubectl with its context set. Simply copy and paste the `config` file
in the .kubernetes folder.
<br><br>
If you have Kubernetes running on Docker for Mac and you want to use it, you can
find your config file by running `ls $HOME/.kube` in your terminal.
"""
import os
import json
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.models import Variable

# Set up a DAG
default_args = {
    'start_date': datetime(2015, 12, 1),
    'trigger_rule': 'all_success'
}
dag = DAG(
    'Example_3',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
)
dag.doc_md = __doc__

KubernetesPodOperator(
    task_id='Run_Kubernetes_Pod',
    image='hello-world',
    namespace='default',
    name='hello-world',
    dag=dag
)
