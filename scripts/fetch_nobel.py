import requests
import os
import time
import json
category = 'med'
endpoint = "https://api.nobelprize.org/2.1/laureates"
OUTPUT_PATH = os.path.join('data', 'raw', 'laureates_raw.json')

def fetch_nobel(limit: int =100, sleep_sec: float =0.5):
    all_records = []
    count = None
    offset = 0
    while True:
        #fetch data from endpoint
        params = {'nobelPrizeCategory': category,
                  'limit': limit,
                  'offset': offset}
        response = requests.get(endpoint, params=params, headers={'User-Agent': "fetch-nobel-script/1.0"})
        data = response.json()
        #Append data to all_records
        laureates = data.get('laureates',[])
        all_records.extend(laureates)
        #Stop condition
        if count is None:
            count = data.get('meta',{}).get('count', 0)
        if len(all_records) >= count:
            break

        offset += limit
        time.sleep(sleep_sec)
    return {
        'meta_count': count,
        'laureates': all_records
    }

def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH),exist_ok=True)
    combined_data = fetch_nobel()
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)
    print(f"Saved {combined_data['meta_count']} laureates to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()


