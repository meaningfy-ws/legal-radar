#!/usr/bin/python3

# faiss_multi_indexing_pipeline.py
# Date:  20.10.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

import sys
sys.path.append("/opt/airflow/")
sys.path = list(set(sys.path))
from airflow.decorators import dag, task
from dags.etl_dags import DEFAULT_DAG_ARGUMENTS

REQUIREMENTS_FILE_NAME = 'requirements.txt'

install_requirements = []

with open(REQUIREMENTS_FILE_NAME) as file:
    install_requirements = list(map(str.strip,file.read().splitlines()))


@dag(default_args=DEFAULT_DAG_ARGUMENTS, tags=['etl'])
def create_index_dag(self):
    
    @task.virtualenv(system_site_packages=False,
                     requirements=install_requirements,
                     )
    def create_index():
        import sys
        sys.path.append("/opt/airflow/")
        from legal_radar.services.faiss_indexing_pipeline import FaissIndexingPipeline
        from legal_radar.services.split_documents_pipeline import TEXT_PIECE_EMBEDDING
        from legal_radar.services.store_registry import store_registry

        FAISS_BUCKET_NAME = 'faiss-index'
        FAISS_INDEX_FINREG_NAME = 'faiss_index_finreg'
        FIN_REG_SPLITTED_ES_INDEX = 'ds_finreg_splitted'

        EXPERIMENT_CONFIGS = [
            #(1, 1),
            #(2, 1),
            #(5, 2),
            (10, 5),
            (20, 10),
            (50, 25),
            (100, 50)]
        for split_window_size, split_window_step in EXPERIMENT_CONFIGS:
            fin_reg_es_index_name = '_'.join(
                map(str, (FIN_REG_SPLITTED_ES_INDEX, split_window_size, split_window_step)))
            faiss_index_finreg_name = '_'.join(
                map(str, (FAISS_INDEX_FINREG_NAME, split_window_size, split_window_step, '.pkl')))
            print(fin_reg_es_index_name, faiss_index_finreg_name)
            faiss_indexing_pipeline = FaissIndexingPipeline(es_index_name=fin_reg_es_index_name,
                                                            embedding_column_name=TEXT_PIECE_EMBEDDING,
                                                            result_bucket_name=FAISS_BUCKET_NAME,
                                                            result_faiss_index_name=faiss_index_finreg_name,
                                                            store_registry=store_registry)
            faiss_indexing_pipeline.execute()


    create_index()
    

etl_dag = create_index_dag()()


