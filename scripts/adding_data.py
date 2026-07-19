import json
import re
from curl_cffi import requests as cf_requests
from bs4 import BeautifulSoup
from weasyprint import HTML
import os
import time

with open('data/raw/id_url_mapping.json', "r", encoding="utf-8") as f:
    id_url_mapping = json.load(f)

for id, url in id_url_mapping.items():
    url_advanced_information = re.sub(r'/[a-z0-9-]+/lecture/?$', '/advanced-information/', url)
    pdf_filename = os.path.join('data','raw', f"{id}_nobel_lecture.pdf")
    response = cf_requests.get(url_advanced_information, impersonate= 'chrome', timeout=15)
    if response.status_code != 200:
        continue

    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('article', class_='entry-content')
    if not main_content:
        continue

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
            # Fix Bug #2: Kept destination path and extensions consistent
    HTML(string=clean_html).write_pdf(pdf_filename)
    print(f"   [Success] Rendered Web-to-PDF: {pdf_filename}")
    time.sleep(2)


    

    

