"""
# Example DAG 3
This workflow is an exam
"""
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

# https://people.sc.fsu.edu/~jburkardt/data/csv/biostats.csv

# Set up a DAG
dag = DAG(
    'Example_3',
    schedule_interval=None
)
