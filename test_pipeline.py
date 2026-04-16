import sys
import torch
from transformers import pipeline

try:
    print("Loading model...")
    device = 0 if torch.cuda.is_available() else -1
    classifier = pipeline("text-classification", model="Hello-SimpleAI/chatgpt-detector-roberta", device=device)
    print("SUCCESS")
except Exception as e:
    print("ERROR:", e)
