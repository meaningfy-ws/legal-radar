import pickle
from legal_radar import config
from legal_radar.services.feature_selector import reduce_array_column
from legal_radar.services.store_registry import store_registry
from legal_radar.services.split_documents_pipeline import DOCUMENT_ID_SOURCE
import pandas as pd
from mfy_nlp_core.adapters.abstract_model import SentenceEmbeddingModelABC
import faiss
import numpy as np

DATES_DOCUMENT = 'dates_document'
HTML_LINKS = 'htmls_to_download'
TEXT_PIECE = 'text_piece'
SAMPLE_QUESTIONS_COLUMN = 'Questions/Text Extracts'
SAMPLE_CELEX_NUMBER = 'Celex No'


class SemanticSearchEvaluation:

    def __init__(self,
                 documents_es_index_name: str,
                 splitted_documents_es_index_name: str,
                 faiss_bucket_name: str,
                 faiss_index_path: str,
                 embedding_model: SentenceEmbeddingModelABC,
                 sample_questions_csv_path: str,
                 sample_questions_csv_sep: str,
                 ):
        self.documents_es_index_name = documents_es_index_name
        self.splitted_documents_es_index_name = splitted_documents_es_index_name
        self.faiss_bucket_name = faiss_bucket_name
        self.faiss_index_path = faiss_index_path
        self.embedding_model = embedding_model
        self.sample_questions_csv_path = sample_questions_csv_path
        self.sample_questions_csv_sep = sample_questions_csv_sep
        self.documents = None
        self.splitted_documents = None
        self.faiss_index = None
        self.sample_questions = None

    def load_documents(self):
        """Read the data from ES."""
        es_store = store_registry.es_index_store()
        df = es_store.get_dataframe(index_name=self.documents_es_index_name)
        df[DATES_DOCUMENT] = pd.to_datetime(df[DATES_DOCUMENT]).dt.date
        self.documents = df

    def load_splitted_documents(self):
        """Read the data from ES."""
        es_store = store_registry.es_index_store()
        self.splitted_documents = es_store.get_dataframe(
            index_name=self.splitted_documents_es_index_name)

    def load_faiss_index(self):
        """Load and deserialize the Faiss index."""
        minio_store = store_registry.minio_object_store(
            minio_bucket=self.faiss_bucket_name)
        data = pickle.loads(minio_store.get_object(
            object_name=self.faiss_index_path))
        self.faiss_index = faiss.deserialize_index(data)

    def load_sample_questions(self):
        self.sample_questions = pd.read_csv(
            self.sample_questions_csv_path, sep=self.sample_questions_csv_sep)
        self.sample_questions = self.sample_questions[self.sample_questions[SAMPLE_QUESTIONS_COLUMN].notnull(
        )]

    def semantic_search(self, user_input: str):
        num_results = 100
        embeddings = self.embedding_model.encode(sentences=[user_input])
        D, I = self.faiss_index.search(
            np.array(embeddings).astype("float32"), k=num_results)
        document_parts = pd.DataFrame(
            self.splitted_documents.iloc[I.flatten().tolist()])
        document_parts['similarity'] = pd.Series(D.flatten().tolist()).values
        document_parts = document_parts.drop_duplicates(
            DOCUMENT_ID_SOURCE).reset_index(drop=True)
        documents_id = document_parts[DOCUMENT_ID_SOURCE].values
        result_documents = pd.DataFrame(
            self.documents.loc[documents_id]).reset_index(drop=True)
        result_documents['similarity'] = document_parts['similarity']
        result_documents['text_piece'] = document_parts['text_piece']
        return result_documents

    def find_part_in_search_result(self, result_set: pd.DataFrame, reference_dataset_celex_number: str,
                                   result_set_celex_number: str = 'celex_numbers') -> tuple:
        """Finds the position and the similarity of the documents parts from the result set

        Args:
            result_set (pd.DataFrame): the result dataset from semantic search execution
            reference_dataset_celex_number (str): celex numbers from test bed dataset
            result_set_celex_number (str, optional): [description]. Defaults to 'celex_numbers'.

        Returns:
            tuple: the position and the similarity from document part result set
        """
        reduced_array_dataset = reduce_array_column(
            result_set, result_set_celex_number).reset_index(drop=True)
        index = reduced_array_dataset[
            reduced_array_dataset[result_set_celex_number].isin([reference_dataset_celex_number])].index.to_list()
        position = reduced_array_dataset['text_piece'].loc[index].index.to_list(
        )
        similarity = reduced_array_dataset['similarity'].apply(
            lambda x: 1 / (1 + x)).loc[index].to_list()

        return position, similarity

    def find_document_in_search_result(self, result_set: pd.DataFrame, reference_dataset_celex_number: str,
                                       result_set_celex_number: str = 'celex_numbers') -> list:
        """Finds the position and the similarity of the documents from the result set

        Args:
            result_set (pd.DataFrame): the result dataset from semantic search execution
            reference_dataset_celex_number (str): celex numbers from test bed dataset
            result_set_celex_number (str, optional): [description]. Defaults to 'celex_numbers'.

        Returns:
            list: the position of the document from result set
        """
        reduced_array_dataset = reduce_array_column(
            result_set, result_set_celex_number).reset_index(drop=True)
        index = reduced_array_dataset[
            reduced_array_dataset[result_set_celex_number].isin([reference_dataset_celex_number])].index.to_list()
        position = reduced_array_dataset['title'].loc[index].index.to_list()

        return position

    def evaluate_parts(self, test_bed: pd.DataFrame) -> list:
        """Executes each input query from the test bed dataset into semantic search and grabs the position and
            the similarity of the documents and documents' part of the result set.

        Args:
            test_bed (pd.DataFrame): test dataset with the input queries and comparable celex number

        Returns:
            list: the position and the similarity of the documents and documents' part
        """
        result = []
        for index, row in test_bed.iterrows():
            result_set = self.semantic_search(row[SAMPLE_QUESTIONS_COLUMN])
            position_p, similarity = self.find_part_in_search_result(
                result_set, row[SAMPLE_CELEX_NUMBER])
            position_d = self.find_document_in_search_result(
                result_set, row[SAMPLE_CELEX_NUMBER])
            result.append({
                'position_part': position_p,
                'position_document': position_d,
                'similarity': similarity
            })

        return result

    def merge_test_bed_with_result_set(self, test_bed: pd.DataFrame, result_set: list) -> pd.DataFrame:
        """Merge the test bed dataframe and the result set list into a single dataframe

        Args:
            test_bed (pd.DataFrame): test dataset with the input queries and comparable celex number 
            result_set (list): the result from evaluation part

        Returns:
            pd.DataFrame: merged dataframe from test bed and evaluation part
        """
        result = pd.DataFrame(result_set)
        result = result.assign(in_top_5_slices=result['position_part'].apply(lambda x: any(np.array(x) <= 5)),
                               in_top_10_slices=result['position_part'].apply(
                                   lambda x: any(np.array(x) <= 10)),
                               in_top_5_documents=result['position_document'].apply(
            lambda x: any(np.array(x) <= 5)),
            in_top_10_documents=result['position_document'].apply(
            lambda x: any(np.array(x) <= 10)),
            in_q3=result['similarity'].apply(lambda x: any(np.array(x) >= 0.75)))

        return pd.merge(test_bed, result, on=test_bed.index, how="inner")

    def evaluate(self) -> pd.DataFrame:
        self.load_documents()
        self.load_splitted_documents()
        self.load_faiss_index()
        self.load_sample_questions()
        evaluation = self.evaluate_parts(self.sample_questions)
        result = self.merge_test_bed_with_result_set(
            self.sample_questions, evaluation)
        return result
