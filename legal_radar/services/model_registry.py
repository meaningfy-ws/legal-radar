from abc import ABC, abstractmethod

import mfy_nlp_core
from mfy_nlp_core.adapters.abstract_model import WordEmbeddingModelABC, SentenceEmbeddingModelABC, TokenizerModelABC, \
    DocumentEmbeddingModelABC
from mfy_nlp_core.adapters.embedding_models import SpacyTokenizerModel, BasicTokenizerModel, Word2VecEmbeddingModel, \
    AverageSentenceEmbeddingModel, TfIdfSentenceEmbeddingModel, UniversalSentenceEmbeddingModel, \
    EurLexBertSentenceEmbeddingModel, TfIdfDocumentEmbeddingModel, SpacySentenceSplitterModel, \
    EurLexBertDocumentEmbeddingModel, MovingWindowTextSplitterModel

class EmbeddingModelRegistryABC(ABC):

    @abstractmethod
    def word2vec_law(self) -> WordEmbeddingModelABC:
        raise NotImplementedError

    @abstractmethod
    def sent2vec_avg(self) -> SentenceEmbeddingModelABC:
        raise NotImplementedError

    @abstractmethod
    def sent2vec_tfidf_avg(self) -> SentenceEmbeddingModelABC:
        raise NotImplementedError

    @abstractmethod
    def sent2vec_universal_sent_encoding(self) -> SentenceEmbeddingModelABC:
        raise NotImplementedError

    @abstractmethod
    def sent2vec_eurlex_bert(self) -> SentenceEmbeddingModelABC:
        raise NotImplementedError


class TokenizerModelRegistryABC(ABC):

    @abstractmethod
    def basic_tokenizer(self) -> TokenizerModelABC:
        raise NotImplementedError

    @abstractmethod
    def spacy_tokenizer(self) -> TokenizerModelABC:
        raise NotImplementedError


class TokenizerModelRegistry(TokenizerModelRegistryABC):

    def __init__(self):
        self.nlp = mfy_nlp_core.services.nlp

    def spacy_tokenizer(self) -> TokenizerModelABC:
        return SpacyTokenizerModel(spacy_tokenizer=self.nlp.tokenizer)

    def basic_tokenizer(self) -> TokenizerModelABC:
        return BasicTokenizerModel()


class EmbeddingModelRegistry(EmbeddingModelRegistryABC):

    def __init__(self):
        self.nlp = mfy_nlp_core.services.nlp

    def word2vec_law(self) -> WordEmbeddingModelABC:
        #LanguageModel.LAW2VEC.fetch()
        #law2vec_path = LanguageModel.LAW2VEC.path_to_local_cache()
        l2v_dict = None #KeyedVectors.load_word2vec_format(law2vec_path, encoding="utf-8")
        return Word2VecEmbeddingModel(word2vec=l2v_dict)

    def sent2vec_avg(self) -> SentenceEmbeddingModelABC:
        return AverageSentenceEmbeddingModel(word_embedding_model=self.word2vec_law(),
                                             tokenizer=tokenizer_registry.spacy_tokenizer()
                                             )

    def sent2vec_tfidf_avg(self) -> SentenceEmbeddingModelABC:
        return TfIdfSentenceEmbeddingModel(word_embedding_model=self.word2vec_law(),
                                           tokenizer=tokenizer_registry.spacy_tokenizer()
                                           )

    def sent2vec_universal_sent_encoding(self) -> SentenceEmbeddingModelABC:
        return UniversalSentenceEmbeddingModel()

    def sent2vec_eurlex_bert(self) -> SentenceEmbeddingModelABC:
        return EurLexBertSentenceEmbeddingModel()

    def doc2vec_tfidf_weight_avg(self) -> DocumentEmbeddingModelABC:
        return TfIdfDocumentEmbeddingModel(sent_emb_model=UniversalSentenceEmbeddingModel(),
                                           sent_splitter=SpacySentenceSplitterModel(spacy_nlp=self.nlp),
                                           top_k=10)

    def doc2vec_eurlex_bert(self) -> DocumentEmbeddingModelABC:
        return EurLexBertDocumentEmbeddingModel(text_splitter=MovingWindowTextSplitterModel(window_size=200,
                                                                                            window_step=150))


tokenizer_registry = TokenizerModelRegistry()
embedding_registry = EmbeddingModelRegistry()