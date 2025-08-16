from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# docker compose build --no-cache
# docker compose up -d

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 8, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'scraping_main_run',
    default_args=default_args,
    schedule_interval='@weekly',
    catchup=False
) as dag:

    run_scraping = BashOperator(
        task_id='run_scraping_script',
        # bash_command='cd /opt/airflow/tesis-scraping && source venv/bin/activate && python3 extraccion/main.py'
        # bash_command='cd /opt/airflow/tesis-scraping && ls && venv/bin/python3 extraccion/main.py'
        bash_command='cd /opt/airflow/tesis-scraping && source venv/bin/activate && python extraccion/main.py'


    )
