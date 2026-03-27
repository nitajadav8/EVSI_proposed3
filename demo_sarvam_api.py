
from transformers import AutoTokenizer, AutoModelForCausalLM
import pandas as pd
import json
import torch
from sarvamai import SarvamAI



api_key="sk_vzs6qle8_3WnCHGCgtx37kvOTXQEOtArC"
client = SarvamAI(api_subscription_key=api_key)

####################################################
#prompting and summary function through sarvam 
###################################################

def get_summary(text):

    summary_prompt=f"""
What is the clear and concise summary of the following segment?

{text}

Summary:
"""

    messages = [
                {"role": "system", "content": "You are a educational content summarizing expert. "
                "Provide concise and clear answers after Summary: "},

                {"role": "user", "content": summary_prompt},
                 ]
    
    response = client.chat.completions(model="sarvam-m", messages=messages)
    summary = response.choices[0].message.content.strip()
    return summary

############################################
# ----- JSONL saving utility -----
#######################################

def load_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    return pd.DataFrame(records)

def save_jsonl(df, path):
    with open(path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            f.write(json.dumps(row.to_dict(), ensure_ascii=False) + "\n")

#########################################
# ----- Main_Pipeline -----
########################################

print("reading data...")
val = load_jsonl('En/English_5minSeg.jsonl')
#val["paraSummary"] = val["para_text"].apply(lambda x: summarize_zero_shot(x))
demo1 = [val["m_segment_text"].iloc[0]]
print("-----------------generating paragraph summaries (batched)......................")
demo_summary1 = get_summary(demo1)
print('----------------------------------returned DEMO SUMMARY 1---------------------------------------------------')
print(demo_summary1)
print('------------------')
#save_jsonl(qwen_valsumm_df, "adapt_finalvalsumm.jsonl")

print("done")
