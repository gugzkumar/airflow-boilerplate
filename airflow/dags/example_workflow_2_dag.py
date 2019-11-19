"""
# Example DAG 2
This workflow is an example of how to fetch data from an API, and then send
that data via Slack message.<br><br>

You can change how much data you want to fetch by setting the `NUM_USERS` airflow
Variable (http://localhost:8080/admin/variable/).<br><br>

Tasks communicate with eachother via Xcom. You can read more about xcom here:<br>
[http://airflow.apache.org/concepts.html#xcoms](http://airflow.apache.org/concepts.html#xcoms)
"""
import os
import json
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.slack_operator import SlackAPIOperator,SlackAPIPostOperator
from datetime import datetime, timedelta
from airflow.models import Variable

# Get and Set Configurations
NUM_USERS = Variable.get("NUM_USERS", default_var=5)
SLACK_OAUTH_TOKEN = os.environ['SLACK_OAUTH_TOKEN']

# Set up a DAG
default_args = {
    'start_date': datetime(2015, 12, 1),
    'trigger_rule': 'all_success'
}
dag = DAG(
    'Example_2',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
)
dag.doc_md = __doc__

# Set up our Get Users task
get_users_task = SimpleHttpOperator(
    task_id='Get_Users',
    method='GET',
    endpoint=f'http://api:3000/users/{NUM_USERS}',
    xcom_push=True,
    http_conn_id=None,
    dag=dag,
)

# Set up our Massage Request task
def massage_json_to_slackmessage(ds, **context):
    # Context provides the following macros http://airflow.apache.org/macros.html
    # First get json data from previous task
    task_instance = context['task_instance']
    user_list = json.loads(
        task_instance.xcom_pull(task_ids='Get_Users')
    )
    print('------- JSON Data from Get_Users task -------')
    print(user_list)
    # Transform data into a slackmessage (string)
    user_json_to_message = lambda user: f'*{user["firstName"]} {user["lastName"]}* _({user["email"]})_'
    slackmessage = '\n'.join([
        user_json_to_message(user) for user in user_list
    ])
    task_instance.xcom_push(key='slackmessage', value=slackmessage)

massage_task = PythonOperator(
    task_id='Massage_JSON_To_Slack_Markdown',
    provide_context=True,
    python_callable=massage_json_to_slackmessage,
    dag=dag,
)

# Set up our Send Email task
send_slack_task = SlackAPIPostOperator(
    task_id='Send_Slack_Message',
    token = SLACK_OAUTH_TOKEN,
    channel ='#airflow-boilerplate',
    text ="{{ task_instance.xcom_pull(task_ids='Massage_JSON_To_Slack_Markdown', key='slackmessage') }}",
    dag=dag
)

# Connect the tasks together
get_users_task >> massage_task >> send_slack_task
