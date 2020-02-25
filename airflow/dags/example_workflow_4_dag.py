"""
# Example DAG 4

"""
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# Set up a DAG
default_args = {
    'start_date': datetime(2015, 12, 1)
}
dag = DAG(
    'Example_1',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
)
dag.doc_md = __doc__
