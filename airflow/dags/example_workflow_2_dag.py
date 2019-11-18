"""
# Example DAG 2
This workflow is an exam
"""
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

# Set up a DAG
dag = DAG(
    'Example_2',
    schedule_interval=None
)
dag.doc_md = __doc__
