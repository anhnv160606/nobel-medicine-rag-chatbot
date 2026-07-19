from curl_cffi import requests as cf_requests
import re
from bs4 import BeautifulSoup

response = cf_requests.get('https://www.nobelprize.org/prizes/medicine/2006/press-release/', impersonate='chrome', timeout=15)
if response.status_code != 200:
    print('fail')

soup = BeautifulSoup(response.text, 'html.parser')
main_content = soup.find('article', class_='entry-content')
if not main_content:
    print('no content')

for layout_el in main_content.find_all(['select', 'header', 'aside']):
        layout_el.decompose()

clean_text = main_content.get_text(separator=' ', strip=True)
print(clean_text)