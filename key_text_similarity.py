#find a key text segment similar to reference summary

import psycopg2
import re
import os
import subprocess
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
import pandas as pd

# ================= DB CONFIG =================
DB_CONFIG = {
   "dbname": "Hindi",
    "user": "postgres",
    "password": "nita",
    "host": "localhost",
    "port": 5432
}
# ============================================

# Connect DB
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

cur.execute("""
    SELECT 
    s.merged_name,
    s.video_id,
    s.merged_text,
    v.ai_native_sum
FROM merged_segment_5min s
JOIN video v
ON s.video_id = v.video_id
WHERE s.merged_text IS NOT NULL
AND v.ai_native_sum IS NOT NULL
ORDER BY s.video_id, s.m_segment_id, s.start_time
""")

videos = cur.fetchall()
print(f"found {len(videos)}")

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


results = []

for merged_name, video_id, merged_text, ai_native_sum in videos:

    if not isinstance(merged_text, str):
        continue

    if not isinstance(ai_native_sum, str):
        continue

    if merged_text.strip() == "":
        continue

    if ai_native_sum.strip() == "":
        continue

    # Encode
    emb1 = model.encode(merged_text, convert_to_tensor=True)
    emb2 = model.encode(ai_native_sum, convert_to_tensor=True)

    # Cosine similarity
    score = util.cos_sim(emb1, emb2).item()

    results.append([
        merged_name,
        video_id,
        merged_text,
        score,
        ai_native_sum
    ])


# ======================
# SAVE CSV
# ======================

df = pd.DataFrame(
    results,
    columns=[
        "merged_name",
        "video_id",
        "merged_text",
        "score",
        "ai_native_sum"
    ]
)

df.to_csv(
    "hn_segement_score.csv",
    index=False,
    encoding="utf-8"
)

print("CSV saved: merged_similarity.csv")