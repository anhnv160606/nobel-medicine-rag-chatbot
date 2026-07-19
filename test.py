from src.rag.__init__ import (
    load_documents,
    text_splitter,
    loading_vector_database,
    retriever_from_vector_database,
    generate_answer,
)

documents = load_documents()
chunks = text_splitter(documents, chunk_size=1000, overlap=200)
db = loading_vector_database(chunks)
retriever = retriever_from_vector_database(db, k=3, score_threshold=0.2)
answer = generate_answer(retriever, "Who won the Nobel Prize in Medicine in 2023?")
print(answer)

