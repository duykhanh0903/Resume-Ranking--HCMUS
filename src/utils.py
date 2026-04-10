import os
import json
from sentence_transformers import InputExample

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

def load_data_for_sbert(file_name):
    file_path = os.path.join(PROCESSED_DATA_DIR, file_name)
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
            
    label_map = {"No Fit": 0.0, "Potential Fit": 0.5, "Good Fit": 1.0}
    
    examples = []
    raw_data = [] 
    for item in data:
        score = label_map.get(item['label'], 0.0)
        examples.append(InputExample(texts=[item['job_description_text'], item['resume_text']], label=score))
        raw_data.append({'jd': item['job_description_text'], 'cv': item['resume_text'], 'score': score})
        
    return examples, raw_data