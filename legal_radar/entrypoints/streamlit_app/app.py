import streamlit as st
from langchain.vectorstores.milvus import Milvus
from langchain.embeddings import HuggingFaceEmbeddings
from legal_radar import config

DEFAULT_SEARCH = """The Semantic Interoperability Community develops solutions to help European public administrations perform seamless and meaningful cross-border and cross-domain data exchanges."""
DEFAULT_INDEX = "eurlex"


@st.cache_resource
def load_vector_store():
    embeddings = HuggingFaceEmbeddings(model_name="thenlper/gte-small",
                                       encode_kwargs={'normalize_embeddings': True})
    return Milvus(embedding_function=embeddings, collection_name=DEFAULT_INDEX,
                  connection_args={"host": config.MILVUS_HOST, "port": config.MILVUS_PORT})


def main():
    vector_store = load_vector_store()
    st.title("Legal Radar - semantic search")

    # User search
    user_input = st.text_area("Search box", DEFAULT_SEARCH)
    return_whole_document = st.checkbox("Result similarity for document parts", )
    # Filters
    st.sidebar.markdown("**Filters**")
    # filter_year = st.sidebar.slider("Publication year", 1900, 2021, (1900, 2021), 1)
    num_results = st.sidebar.slider("Number of text parts in sum", 1, 10, 5)

    # Fetch results
    if st.button("Search"):
        # Get paper IDs
        doc_results = vector_store.similarity_search_with_score(user_input, k=num_results)
        print(user_input)
        print(num_results)
        print(doc_results)
        if doc_results:
            # Get individual results
            for document, similarity_rank in doc_results:
                document_metadata = document.metadata
                document_content = document.page_content
                st.write(f"""#### {document_metadata['title']}""")
                st.write(f"""**CELEX-NUMBER:**
                        {document_metadata["doc_id"]}""")

                if return_whole_document:
                    st.write(f"""**Content:**
                            {document_content}""")

                st.write(f"""**Similarity:**
                         {similarity_rank}""")
                st.write(f"""**EurLex link**
                        https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A{document_metadata["doc_id"]}""")
                st.write(f"""---""")


if __name__ == "__main__":
    main()
