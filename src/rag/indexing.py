from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy 

def loading_vector_database(documents: list[Document], model_name: str = "BAAI/bge-small-en-v1.5"):
    
    embedding_wrapper = HuggingFaceEmbeddings(
        model_name = model_name,
        model_kwargs = {"device": "cpu"},
        encode_kwargs = {"normalize_embeddings": True, 'batch_size': 32},
    )

    db = FAISS.from_documents(documents, embedding_wrapper, distance_strategy=DistanceStrategy.COSINE)

    return db




