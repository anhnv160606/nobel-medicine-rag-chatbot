from langchain_community.vectorstores import FAISS

def retriever_from_vector_database(db: FAISS, k: int = 3, score_threshold: float = 0.2):
    
    retriever = db.as_retriever(
        search_type = 'similarity_score_thresold',
        search_kwargs = {"k": k, 'score_threshold': score_threshold}
    )

    return retriever

