import requests
import xmltodict
import json
from time import sleep
from tqdm import tqdm
import os
import sys

ID_LIST_FILE = "documents_in_oa_serials.csv"  # Input file with IDs
OUTPUT_FILE = "records-oa-100.jsonl"         # Output JSONL file
MAX_RECORDS = 100                            # Limit to first N IDs (None for all)
SLEEP_TIME = 1                               # Seconds between requests
HEADERS = {"User-Agent": "zbMATH-OAI-Harvester/1.0"}
BASE_URL_TEMPLATE = "https://oai.zbmath.org/v1/?verb=GetRecord&identifier=oai:zbmath.org:{id}&metadataPrefix=oai_zb_preview"


def harvest_zbmath_by_id_list(id_file=ID_LIST_FILE,
                              output_file=OUTPUT_FILE,
                              max_records=MAX_RECORDS,
                              sleep_time=SLEEP_TIME):
    # Read all IDs from input file
    with open(id_file, "r", encoding="utf-8") as f:
        ids = [line.strip() for line in f if line.strip()]

    if max_records:
        # ids = ids[:max_records]
        ids = ids[100:]

    # Determine already processed IDs (resume support)
    processed_ids = set()
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f_out:
            for line in f_out:
                try:
                    record = json.loads(line)
                    # Assuming the zbMATH ID is stored at record['header']['identifier']
                    identifier = record.get("header", {}).get("identifier", "")
                    if identifier.startswith("oai:zbmath.org:"):
                        processed_ids.add(identifier.split(":")[-1])
                except json.JSONDecodeError:
                    continue

    remaining_ids = [i for i in ids if i not in processed_ids]

    if not remaining_ids:
        print("✅ All IDs already processed. Nothing to do.")
        return

    print(f"🔄 Resuming harvest. {len(processed_ids)} already fetched, {len(remaining_ids)} remaining.")

    total_count = len(processed_ids)
    with open(output_file, "a", encoding="utf-8") as f_out:
        pbar = tqdm(remaining_ids, desc="Fetching records", unit="record")
        for zb_id in pbar:
            url = BASE_URL_TEMPLATE.format(id=zb_id)
            try:
                response = requests.get(url, headers=HEADERS, timeout=(5,30))
                if response.status_code != 200:
                    print(f"⚠️ Error fetching ID {zb_id}: HTTP {response.status_code}")
                    continue

                data = xmltodict.parse(response.content)
                record = data.get("OAI-PMH", {}).get("GetRecord", {}).get("record", {})

                if not record:
                    print(f"⚠️ No record found for ID {zb_id}")
                    continue

                # Write as JSON line immediately (ensures saving even if interrupted)
                json_line = json.dumps(record, ensure_ascii=False)
                f_out.write(json_line + "\n")
                f_out.flush()

                total_count += 1
                sleep(sleep_time)

            except KeyboardInterrupt:
                print("\n⏹ Interrupted by user. Progress saved.")
                break
            except Exception as e:
                print(f"❌ Failed for ID {zb_id}: {e}")
                continue

    print(f"\n✅ Done. {total_count} total records saved to {output_file}")


if __name__ == "__main__":
    harvest_zbmath_by_id_list()
