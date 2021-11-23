
import sys
sys.path.append("/opt/airflow/")
sys.path = list(set(sys.path))
from airflow.decorators import dag, task
from dags.etl_dags import DEFAULT_DAG_ARGUMENTS


@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['etl'])
def test_dag_with_task():
    
    @task
    def first_step():
        print("Enter in venv")
        import sys
        sys.path.append("/opt/airflow/")
        #from legal_radar import config
        #print(config.ELASTICSEARCH_USERNAME)
        return {"one": "Hello", "two": "World"}

    @task()
    def second_step(data: dict):
        print("Recieved data:")
        for key in data.keys():
            print(f"{key}:{data[key]}")

    tmp = first_step()
    second_step(tmp)


etl_dag = test_dag_with_task()


