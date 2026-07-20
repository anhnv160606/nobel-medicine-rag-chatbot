import glob
import json
import fitz
import os
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def build_metadata_header(meta: dict) -> str:
    return (
        f"[Laureate: {meta.get('laureate_name', 'Unknown')} | "
        f"Award Year: {meta.get('award_year', 'Unknown')} | "
        f"Country: {meta.get('laureate_country', 'Unknown')} | "
        f"Motivation: {meta.get('motivation', 'Unknown')}]\n\n"
    )


def load_documents():

    with open('data/processed/metadata_lookup.json', "r", encoding="utf-8") as f:
        metadata_lookup = json.load(f)

    documents = []
    pdf_files = glob.glob('data/raw/*.pdf')
    for filepath in pdf_files:
        filename = os.path.basename(filepath)  
        id = filename.replace("_nobel_lecture.pdf", "").lower()
        
        doc = fitz.open(filepath)
        full_text = ""
        
        for page in doc:
            full_text += page.get_text("text") + "\n"

        header = build_metadata_header(metadata_lookup.get(id, {})) 
        
        lecture_doc = Document(
            page_content= header + full_text,
            metadata={
                "id": id,
                "laureate_name": metadata_lookup.get(id, {}).get("laureate_name", "Unknown"),
                "laureate_country": metadata_lookup.get(id, {}).get("laureate_country", "Unknown"),
                "laureate_birthday": metadata_lookup.get(id, {}).get("laureate_birthday", "Unknown"),
                "laureate_deathday": metadata_lookup.get(id, {}).get("laureate_deathday", "Unknown"),
                "award_year": metadata_lookup.get(id, {}).get("award_year", "Unknown"),
                "motivation": metadata_lookup.get(id, {}).get("motivation", "Unknown"),
                "doc_type": 'nobel_lecture'
            }
        )

        press_release_doc = Document(
            page_content= header + metadata_lookup.get(id, {}).get("press_release", "No press release available"),
            metadata={
                "id":id,
                "laureate_name": metadata_lookup.get(id, {}).get("laureate_name", "Unknown"),
                "laureate_country": metadata_lookup.get(id, {}).get("laureate_country", "Unknown"),
                "laureate_birthday": metadata_lookup.get(id, {}).get("laureate_birthday", "Unknown"),
                "laureate_deathday": metadata_lookup.get(id, {}).get("laureate_deathday", "Unknown"),
                "award_year": metadata_lookup.get(id, {}).get("award_year", "Unknown"),
                "motivation": metadata_lookup.get(id, {}).get("motivation", "Unknown"),
                "doc_type": 'press_release'
            }
        )

        documents.append(lecture_doc)
        documents.append(press_release_doc)
    return documents

def text_splitter(documents: list[Document] , chunk_size: int = 1000, overlap: int = 200):    
    MARKDOWN_SEPARATORS = [
    "\n#{1,6} ",
    "```\n",
    "\n\\*\\*\\*+\n",
    "\n---+ \n",
    "\n___+\n",
    "\n\n",
    "\n",
    " ",
    "",
    ]

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        add_start_index=True,
        strip_whitespace=True,
        separators=MARKDOWN_SEPARATORS
    )

    print(f"Chunking {len(documents)} source documents...")
    chunked_docs = text_splitter.split_documents(documents)
    print(f"Created {len(chunked_docs)} chunks.")

    return chunked_docs

if __name__ == "__main__":
    documents = load_documents()
    chunked_docs = text_splitter(documents)
    print(f"Chunked {len(documents)} documents into {len(chunked_docs)} chunks.")
    print(chunked_docs[0].metadata)
    print("+++++++++++++++++++++++++++")
    print(chunked_docs[0].page_content)

    






