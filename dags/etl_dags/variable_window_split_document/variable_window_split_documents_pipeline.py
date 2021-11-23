#!/usr/bin/python3

# variable_window_split_documents_pipeline.py
# Date:  20.10.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

import sys
sys.path.append("/opt/airflow/")
sys.path = list(set(sys.path))
from airflow.decorators import dag, task
from dags.etl_dags import DEFAULT_DAG_ARGUMENTS
import os
os.chdir('/opt/airflow/dags/etl_dags/variable_window_split_document/')

REQUIREMENTS_FILE_NAME = 'requirements.txt'
install_requirements = []
with open(REQUIREMENTS_FILE_NAME) as file:
    install_requirements = list(map(str.strip,file.read().splitlines()))


@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['etl'])
def windowed_split_dag():
    @task.virtualenv(system_site_packages=False,
                     requirements=install_requirements,
                     )
    def windowed_split():
        import sys
        sys.path.append("/opt/airflow/")
        from legal_radar import config
        from legal_radar.services.split_documents_pipeline import WindowedSplitDocumentsPipeline
        from legal_radar.services.model_registry import EmbeddingModelRegistry
        from legal_radar.services.store_registry import store_registry

        TEXTUAL_COLUMNS = ['title', 'content']
        FIN_REG_SPLITTED_ES_INDEX = 'ds_finreg_splitted'

        EXPERIMENT_CONFIGS = [
            #(1, 1),
            #(2, 1),
            #(5, 2),
            #(10, 5),
            (20, 10),
            (50, 25),
            (100, 50)]
        for split_window_size, split_window_step in EXPERIMENT_CONFIGS:
            result_es_index_name = '_'.join(map(str, (FIN_REG_SPLITTED_ES_INDEX, split_window_size, split_window_step)))
            print(f'Start document splitter for: {result_es_index_name}')
            windowed_split_documents_pipeline = WindowedSplitDocumentsPipeline(
                dataset_es_index_name=config.EU_FINREG_CELLAR_ELASTIC_SEARCH_INDEX_NAME,
                result_es_index_name=result_es_index_name,
                textual_columns=TEXTUAL_COLUMNS,
                split_window_size=split_window_size,
                split_window_step=split_window_step,
                store_registry=store_registry,
                embedding_model_registry=EmbeddingModelRegistry())
            windowed_split_documents_pipeline.execute()

    windowed_split()
    

etl_dag = windowed_split_dag()

