import json
import os

def id_url_mapping(json_file_path):
    with open(json_file_path, "r", encoding= 'utf-8') as file:
        data = json.load(file)

    url_mapping = {}
    laureates_list = data['laureates']

    for laureate in laureates_list:
        laureate_id = laureate.get('id')
        for prize in laureate.get('nobelPrizes', []):
            for link in prize.get('links'):
                heref = link.get('href', '')
            
                if 'facts/' in heref:
                    lecture_url = heref.replace('facts/', 'lecture/')
                    url_mapping[laureate_id] = lecture_url
                    break

    with open('id_url_mapping.json', 'w', encoding='utf-8') as f:
        # indent=4 formats the JSON so it is easily readable by humans
        # ensure_ascii=False ensures any special characters in names/URLs render correctly
        json.dump(url_mapping, f, indent=4, ensure_ascii=False)

id_url_mapping('data/raw/laureates_raw.json')



