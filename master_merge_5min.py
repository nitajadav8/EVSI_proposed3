#merging all 5 min segment source+ nptel+ other 

import pandas as pd
import json
import os
import csv
import sys

#csv.field_size_limit(sys.maxsize)

OUTPUT_JSONL = "Te/Telugu_5minSeg.jsonl"


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def get_last_id(jsonl_file):
    if not os.path.exists(jsonl_file):
        return 0

    last_id = 0
    with open(jsonl_file, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            last_id = obj.get("cmerge_id", last_id)

    return last_id


def append_csv_to_jsonl(csv_file):

    source_name = os.path.basename(csv_file)

    df = pd.read_csv(csv_file,engine="python",quoting=csv.QUOTE_MINIMAL)

    start_id = get_last_id(OUTPUT_JSONL)
    cmerge_id = start_id

    with open(OUTPUT_JSONL, "a", encoding="utf-8") as out:
        
        for _, row in df.iterrows():

            cmerge_id += 1

            record = {
                "cmerge_id": cmerge_id,
                "source": source_name,
                "video_id": str(row["video_id"]).strip(),
                "m_segment_id": str(row["merged_segment_id"]).strip(),
                "m_name":str(row["merged_name"]).strip(),
                "m_segment_text":str(row["translated_passage"]).strip()       #translated_passage  merged_segment_text
            
            }

            out.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Finished processing {csv_file}")
    print(f"Records appended. Last combined_id = {cmerge_id}")


if __name__ == "__main__":

    csv_file=r"Te\Ta2Temerge_transcript.csv"                             #Te2Enmerge_translated.csv"

    append_csv_to_jsonl(csv_file)