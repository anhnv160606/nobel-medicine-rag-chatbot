import os
import time
import json
from bs4 import BeautifulSoup
from weasyprint import HTML
from curl_cffi import requests as cf_requests

# Define target paths
RAW_DIR = os.path.join('data', 'raw')
LAUREATES_JSON = os.path.join(RAW_DIR, 'laureates_raw.json')
MAPPING_JSON = os.path.join(RAW_DIR, 'id_url_mapping.json')

# Ensure the download directory exists completely
os.makedirs(RAW_DIR, exist_ok=True)

# Load data safely
with open(LAUREATES_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)
with open(MAPPING_JSON, 'r', encoding="utf-8") as file:
    data_url = json.load(file)


def download_nobel_lecture(laureate_id: str) -> bool:
    """
    Fetches a Nobel lecture by ID. Tries to pull a native PDF first; 
    falls back to rendering the clean HTML article block to a PDF if no link exists.
    Returns True if successfully processed/skipped, False if failed.
    """
    # Fix Bug #1: Explicitly force string keys for JSON mapping safely
    endpoint = data_url.get(str(laureate_id))
    if not endpoint:
        print(f"   [Error] No registered URL mapping found for ID: {laureate_id}")
        return False
        
    # Standard output filename definition to keep both workflows uniform
    pdf_filename = os.path.join(RAW_DIR, f"{laureate_id}_nobel_lecture.pdf")
    
    # Early escape if already processed to save bandwidth and compute
    if os.path.exists(pdf_filename):
        print(f"   [Skipped] Already exists: {pdf_filename}")
        return True

    # 1. Fetch the landing page
    try:
        response = cf_requests.get(endpoint, impersonate='chrome', timeout=15)
        if response.status_code != 200:
            print(f"   [Error] HTTP Status {response.status_code} for ID: {laureate_id}")
            return False
    except Exception as e:
        print(f"   [Error] Connection dropped for ID {laureate_id}: {e}")
        return False

    soup = BeautifulSoup(response.text, 'html.parser')

    # 2. Extract PDF Link
    pdf_link = None
    for a_tag in soup.find_all('a', href=True):
        if '.pdf' in a_tag['href'].lower():
            pdf_link = a_tag['href']
            break # Fix Bug #3: Escape immediately on first matching lecture PDF

    # 3. Execution Path A: Fallback to HTML Scraping if no Native PDF exists
    if not pdf_link:
        main_content = soup.find('article', class_='entry-content')
        
        # Fix Bug #4: Defensive programming against unique/unstructured layouts
        if not main_content:
            print(f"   [Warning] Layout mismatch: Neither PDF nor 'entry-content' found for ID {laureate_id}")
            return False
            
        # Clean layout headers/footers
        for layout_el in main_content.find_all(['select', 'header', 'aside']):
            layout_el.decompose()
            
        clean_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 2.5em; }}
                h2 {{ color: #111; font-size: 24px; }}
                h3 {{ color: #444; font-size: 18px; line-height: 1.4; }}
                p {{ font-size: 14px; text-align: justify; margin-bottom: 12px; }}
            </style>
        </head>
        <body>
            {main_content.prettify()}
        </body>
        </html>
        """
        try:
            # Fix Bug #2: Kept destination path and extensions consistent
            HTML(string=clean_html).write_pdf(pdf_filename)
            print(f"   [Success] Rendered Web-to-PDF: {pdf_filename}")
            return True
        except Exception as e:
            print(f"   [Error] WeasyPrint rendering failed for ID {laureate_id}: {e}")
            return False
    
    # 4. Execution Path B: Download Native PDF Asset
    if pdf_link.startswith('/'):
        pdf_link = "https://www.nobelprize.org" + pdf_link

    try:
        pdf_response = cf_requests.get(pdf_link, impersonate='chrome', timeout=20)
        if pdf_response.status_code == 200:
            with open(pdf_filename, 'wb') as f:
                f.write(pdf_response.content)
            print(f"   [Success] Downloaded Native PDF: {pdf_filename}")
            return True
        else:
            print(f"   [Error] Target PDF URL returned HTTP {pdf_response.status_code}")
            return False
    except Exception as e:
        print(f"   [Error] File stream failed for ID {laureate_id}: {e}")
        return False


# --- BATCH EXECUTION LOOP CONTROLLER ---
if __name__ == "__main__":
    print("="*60)
    print(f"STARTING NOBEL LECTURE PIPELINE ({len(data_url)} total profiles mapped)")
    print("="*60)
    
    success_count = 0
    failure_count = 0
    
    # Loop over every unique ID found inside your mapping configuration file
    for index, current_id in enumerate(data_url.keys(), start=1):
        print(f"[{index}/{len(data_url)}] Processing Laureate ID: {current_id}...")
        
        # Run worker function
        status = download_nobel_lecture(current_id)
        
        if status:
            success_count += 1
        else:
            failure_count += 1
            
        # Pacing: Sleeping for 1.5 seconds keeps scraping footprint perfectly human-like 
        time.sleep(1.5)