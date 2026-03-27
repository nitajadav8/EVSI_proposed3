#qwen from hf
from transformers import AutoTokenizer, AutoModelForCausalLM
import pandas as pd
import json
import torch

model_name = "Qwen/Qwen3-30B-A3B-Instruct-2507"

print(torch.cuda.is_available())

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)

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
    
    text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    # conduct text completion
    generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=16384
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

    content = tokenizer.decode(output_ids, skip_special_tokens=True)
    summary = content.strip()
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
val = load_jsonl('English_5minSeg.jsonl')
#val["paraSummary"] = val["para_text"].apply(lambda x: summarize_zero_shot(x))
demo1 = [val["m_segment_text"].iloc[0]]
print("-----------------generating paragraph summaries (batched)......................")
demo_summary1 = get_summary(demo1)
print('----------------------------------returned DEMO SUMMARY 1---------------------------------------------------')
print(demo_summary1)
print('------------------')
with open('qwn_sum.txt', 'w') as f:
    f.write(demo_summary1)
#save_jsonl(qwen_valsumm_df, "adapt_finalvalsumm.jsonl")

print("done")
