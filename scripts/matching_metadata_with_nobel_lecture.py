import os
import glob
import json
import fitz 
from langchain_core.documents import Document

with open('data/raw/metadata_lookup.json', "r", encoding="utf-8") as f:
    metadata_lookup = json.load(f)

documents = []
pdf_files = glob.glob('data/raw/*.pdf')

for filepath in pdf_files:
    filename = os.path.basename(filepath)  
    
    file_key = filename.replace("_nobel_lecture.pdf", "").lower()
    
    # Retrieve the JSON metadata
    lecture_metadata = metadata_lookup.get(file_key, {"source_id": filename, "status": "No JSON match"})
    
    # Extract text from the PDF using the full filepath
    doc = fitz.open(filepath)
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"
        
    # Create the Document object
    doc_object = Document(
        page_content=full_text,
        metadata=lecture_metadata
    )
    documents.append(doc_object)

