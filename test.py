from src.rag.__init__ import (
    load_documents,
    text_splitter,
    loading_vector_database,
    retriever_from_vector_database,
    generate_answer,
)

documents = load_documents()
chunks = text_splitter(documents, chunk_size=1000, overlap=200)
print('start embedding')
db = loading_vector_database(chunks)
print('load vector database success')
db_path = 'faiss_index_local'
db.save_local(db_path)
print('save file success')
