#!/usr/bin/python3

# split_documents_pipeline.py
# Date:  25.08.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com

import sys
import concurrent.futures
import hashlib
from typing import List

import pandas as pd
import nltk
from more_itertools import windowed

from legal_radar.services.model_registry import EmbeddingModelRegistryABC
from legal_radar.services.store_registry import StoreRegistryABC

TEXTUAL_DATA = 'text_data'
TEXT_PIECE = 'text_piece'
DOCUMENT_ID_SOURCE = 'document_id_source'
TEXT_PIECE_EMBEDDING = 'text_piece_embedding'

class WindowedSplitDocumentsPipeline:

    def __init__(self, dataset_es_index_name: str,
                 result_es_index_name: str,
                 textual_columns: List[str],
                 split_window_size: int,
                 split_window_step: int,
                 store_registry: StoreRegistryABC,
                 embedding_model_registry: EmbeddingModelRegistryABC):
        self.dataset_es_index_name = dataset_es_index_name
        self.result_es_index_name = result_es_index_name
        self.store_registry = store_registry
        self.embedding_model_registry = embedding_model_registry
        self.textual_columns = textual_columns
        self.split_window_size = split_window_size
        self.split_window_step = split_window_step
        self.dataset = None
        self.result_dataset = None

    def load_dataset(self):
        es_store = self.store_registry.es_index_store()
        self.dataset = es_store.get_dataframe(self.dataset_es_index_name)
        self.dataset = self.dataset[self.textual_columns]
        self.dataset.dropna(inplace=True)

    def prepare_textual_data(self):
        for textual_column in self.textual_columns:
            self.dataset = self.dataset[
                self.dataset[textual_column].apply(lambda x: len(x) > 1)]
        self.dataset[TEXTUAL_DATA] = self.dataset[self.textual_columns].agg(lambda texts:
                                                                            ". ".join(texts),
                                                                            axis=1)

    def split_documents_and_store(self):
        emb_model = self.embedding_model_registry.sent2vec_universal_sent_encoding()

        def split_documents_worker(index, value, window_size, window_step):
            try:
                if len(value)==0:
                    return None
                es_store = self.store_registry.es_index_store()
                sentences = nltk.sent_tokenize(value)
                windowed_texts = list(
                    windowed(sentences,
                            n=window_size,
                            fillvalue='',
                            step=window_step)
                )
                del sentences
                result_df = pd.DataFrame()
                for windowed_text in windowed_texts:
                    text_piece = ' '.join(windowed_text)
                    new_index = hashlib.sha256((index + text_piece).encode('utf-8')).hexdigest()
                    result_df.loc[new_index, TEXT_PIECE] = text_piece
                    result_df.loc[new_index, DOCUMENT_ID_SOURCE] = index
                result_df[TEXT_PIECE_EMBEDDING] = emb_model.encode(result_df[TEXT_PIECE].values)
                es_store.put_dataframe(index_name=self.result_es_index_name,
                                    content=result_df
                                    )
                del result_df
                del windowed_text
            except:
                print("Some error in split_documents_worker")
                
            return None

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(split_documents_worker,
                                        index,
                                        value,
                                        self.split_window_size,
                                        self.split_window_step
                                        )
                        for index, value in self.dataset[TEXTUAL_DATA].items()
                        ]
            
                for future in futures:
                    future.result()
        except:
            print("Error in concurrent.futures zone!")
    
    def execute(self):
        self.load_dataset()
        self.prepare_textual_data()
        self.split_documents_and_store()
        # self.compute_embeddings()
        # self.store_splitted_documents()
