import requests
import json
import time

BASE_URL = "https://api.zbmath.org/v1"
HEADERS = {"Accept": "application/json"}
OUTPUT_FILE = "msc_codes.json"
PAGE_SIZE = 500  # max per API

def fetch_msc_codes(page=0, size=PAGE_SIZE):
    params = {
        "page": page,
        "results_per_page": size,
        "Level": 2
    }
    response = requests.get(f"{BASE_URL}/classification/_structured_search", headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()

def save_msc_codes_incremental(output_file):
    page = 0
    total_fetched = 0

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("[\n")  # start JSON array

        first_item = True
        while True:
            print(f"Fetching page {page}...")
            data = fetch_msc_codes(page)
            results = data.get("result", [])
            if not results:
                break

            for entry in results:
                # Extract only the specified keys, if present
                filtered_entry = {k: entry[k] for k in ["code", "level", "long_title", "parent", "short_title", "zbmath_url"] if k in entry}

                if not first_item:
                    f.write(",\n")
                else:
                    first_item = False
                
                json.dump(filtered_entry, f, ensure_ascii=False)
                total_fetched += 1
            
            page += 1
            time.sleep(0.5)  # be polite

        f.write("\n]\n")  # end JSON array

    print(f"Saved {total_fetched} MSC codes to {output_file}")

if __name__ == "__main__":
    save_msc_codes_incremental(OUTPUT_FILE)
