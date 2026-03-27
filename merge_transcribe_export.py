#get merged_segment_data with transcribe text only
import psycopg2
import csv
import os
import fitz


DB_CONFIG = {
   "dbname": "English",
    "user": "postgres",
    "password": "nita",
    "host": "localhost",
    "port": 5432
}

OUTPUT_CSV = "Enmerge_transcript.csv"

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

cur.execute("""
        SELECT
            m.video_id,
            v.ai_en_sum,
            m.m_segment_id,
            m.merged_name,
            m.merged_text
        FROM merged_segment_5min m
        JOIN video v
          ON m.video_id = v.video_id
        ORDER BY m.video_id, m.m_segment_id, m.start_time;
    """)

rows = cur.fetchall()

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "video_id",
            "merged_segment_id",
            "merged_name",
            "video_ai_summary",
            "merged_segment_text"
        ])

        for video_id, ai_en_sum, merged_segment_id, merged_name, merged_text in rows:
            if not ai_en_sum:
                print(f"[SKIP] Missing data for video_id={video_id}")    
                #continue

            writer.writerow([
                video_id,
                merged_segment_id,
                merged_name,
                ai_en_sum,
                merged_text.strip()
            ])

# with open(OUTPUT_CSV,"w", newline='', encoding='utf-8') as w:
#     writer=csv.writer(w)
#     writer.writerow([
#         "ctrans_id",
#         "transcript",
#         "reference_summary"
#     ])

#     for trans_id, trans_path, ai_ref_sum in rows:
#         if not trans_path:
#             continue

#         if not os.path.isfile(trans_path):
#             print("file not found: {trans_path}")
#             continue 

#         with open(trans_path, "rb") as f:
#             transcript=extract_pdf_text(trans_path) if trans_path.endswith('.pdf') else read_txt(trans_path)

#         writer.writerow([
#             trans_id,
#             transcript,
#             ai_ref_sum
#         ])

cur.close()
conn.close()

print(f"CSV successfully written to: {OUTPUT_CSV}")
