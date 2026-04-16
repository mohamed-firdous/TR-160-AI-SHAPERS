import sys
import os
sys.path.append(os.getcwd())
import torch
from model.ai_detector import gpt_model, gpt_tokenizer, compute_entropy_variance

def get_ppl(text):
    encodings = gpt_tokenizer(text, return_tensors='pt')
    input_ids = encodings.input_ids
    with torch.no_grad():
        outputs = gpt_model(input_ids, labels=input_ids)
        return torch.exp(outputs.loss).item()

wiki = "The Roman Empire was the post-Republican period of ancient Rome. As a polity, it included large territorial holdings around the Mediterranean Sea in Europe, North Africa, and Western Asia, ruled by emperors."
ai = "In conclusion, the integration of AI into educational systems is not merely an option but a necessity for modern pedagogical success."

print("WIKI PPL:", get_ppl(wiki))
print("WIKI ENT VAR:", compute_entropy_variance(wiki))
print("AI PPL:", get_ppl(ai))
print("AI ENT VAR:", compute_entropy_variance(ai))
