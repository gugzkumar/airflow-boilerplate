"""
# Example DAG 1
In this worklow the Success Task runs if the Start Task exits successfully. <br>
In this worklow the Failiure Task runs if the Start Task exits as a failiure. <br>
<br>
To test the failiure operator set the `bash_command` in the start_task to:<br>
`sleep 5 && echo "Hello World" && exit 0`
<br><br>
To test the failiure operator set the `bash_command` in the start_task to:<br>
`sleep 5 && echo "Hello World" && exit 1`
<br><br>
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
    # schedule_interval='* * * * *', # Uncomment to run every minute
    catchup=False
)
dag.doc_md = __doc__


# Set up a Bash Task that Prints and exits
start_task = BashOperator(
    task_id='Start',
    bash_command='sleep 5 && echo "Hello World" && exit 1',
    dag=dag,
)

# Set up a Python Task that runs if the Bash Operator is successfull
def on_success(ds, **kwargs):
    print('The start task ran successfully')

success_task = PythonOperator(
    task_id='Success',
    provide_context=True,
    python_callable=on_success,
    trigger_rule='all_success',
    dag=dag,
)


# Set up a Python Task that runs if the Bash Operator fails
def on_failiure(ds, **kwargs):
    print('The start task failed')

failiure_task = PythonOperator(
    task_id='Failiure',
    provide_context=True,
    python_callable=on_failiure,
    trigger_rule='all_failed',
    dag=dag,
)

# Connect the tasks together
start_task >> [success_task, failiure_task]
