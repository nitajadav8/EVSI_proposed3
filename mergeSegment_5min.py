#merging with sentence completion and duration of atleast 5min
import psycopg2
import re
import os
import subprocess
from pathlib import Path

# ================= DB CONFIG =================
DB_CONFIG = {
   "dbname": "English",
    "user": "postgres",
    "password": "nita",
    "host": "localhost",
    "port": 5432
}
# ============================================

SENTENCE_END_REGEX = re.compile(r"[.!?\u0964\u06D4]\s*$")
MAX_MERGE_DURATION = 300.0  # seconds (safety) 5min


def create_merged_video(input_video, start, end, output_path):

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-ss", str(start),
        "-to", str(end),
        "-c", "copy",
        output_path
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(e)
    return False


def is_sentence_complete(text):
    if not text:
        print("segment text problem")
        return False
    #print(bool(SENTENCE_END_REGEX.search(text.strip())))
    return bool(SENTENCE_END_REGEX.search(text.strip()))


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Fetch segments ordered properly
    cur.execute("""
        SELECT s.segment_id,
       s.video_id,
       s.start_time,
       s.end_time,
       s.text_segment,
       v.file_path
    FROM segment s
JOIN video v ON s.video_id = v.video_id
WHERE s.text_segment IS NOT NULL
ORDER BY s.video_id, s.start_time;

    """)

    # cur.execute("""
    #             SELECT s.segment_id,
    #    s.video_id,
    #    s.start_time,
    #    s.end_time,
    #    s.text_segment,
    #    v.file_path
    #     FROM segment s
    # JOIN video v ON s.video_id = v.video_id
    # WHERE s.text_segment IS NOT NULL
    # AND s.video_id IN (167,170,175,177,179,180,181,182,185,188,189,195,196)
    # ORDER BY s.video_id, s.start_time;
    #             """)
    

    rows = cur.fetchall()
    print("found videos",len(rows))

    current_video = None
    buffer_text = []
    buffer_start = None
    buffer_end = None
    merge_idx = 1
    input_video_path = None

    OUTPUT_DIR = r"D:\Video_Lecture\English\Derived\merged_segment_5min"

    for seg_id, video_id, start, end, text, video_path in rows:
        

        if not os.path.exists(video_path):
            print("missing file",video_id, video_path)

        # New video → reset buffers
        if video_id != current_video:
            print("starting video", video_id)
            buffer_text = []
            buffer_start = None
            buffer_end = None
            merge_idx = 1
            current_video = video_id
            input_video_path = video_path

        # Initialize buffer
        if buffer_start is None:
            buffer_start = start

        buffer_text.append(text.strip())
        buffer_end = end


        duration = buffer_end - buffer_start
        #print(duration)

        # Merge termination condition
        if is_sentence_complete(text) and duration >= MAX_MERGE_DURATION:
              #print("segment is fine",video_id+seg_id)

              merged_name = f"En_{video_id}_{merge_idx:03d}" #N for nptel, B for Bengali (first ltr of lang yt video)

            # ---- CREATE MERGED VIDEO FILE ----
              out_dir = os.path.join(OUTPUT_DIR, str(video_id))
              output_video_path = os.path.join(
                out_dir, f"{merged_name}.mp4"
            )
              #print("creating", merged_name)
              if not os.path.exists(output_video_path):
                #print("was missing", output_video_path)

                merged_text = " ".join(buffer_text)
          
                status=create_merged_video(
                    input_video_path,
                    buffer_start,
                    buffer_end,
                    output_video_path
                )

                if status is False:
                    print("error for", video_id)
            

            # ---- INSERT INTO DB ----
                else:
                    cur.execute("""
                    INSERT INTO merged_segment_5min (
                    video_id,
                    merged_name,
                    start_time,
                    end_time,
                    merged_text,
                    video_segment_path
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                video_id,
                merged_name,
                buffer_start,
                buffer_end,
                merged_text,
                output_video_path
                ))

              conn.commit()
              #print(buffer_start)

        # else:
        #     print("not segment", video_id, seg_id)

            # Reset buffer
              buffer_text = []
              buffer_start = None
              buffer_end = None
              merge_idx += 1
        
        


    cur.close()
    conn.close()
    print("Segment text + video merging completed successfully.")

if __name__ == "__main__":
    main()