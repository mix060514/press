from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG
from pendulum import datetime

with DAG(
    dag_id="intel_dag",
    schedule="0 8 * * *",
    description="Intel DAG",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['crawl'],
) as dag:
    t1 = BashOperator(
        task_id="run_intel_spider",
        bash_command="cd /home/mix060514/pj/press && source .venv/bin/activate && scrapy crawl intel -a start_page=1 --logfile /home/mix060514/pj/press/logs/intel_$(date +%Y-%m-%d).log"
    )
