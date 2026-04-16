import sys
from transformers import pipeline

classifier = pipeline("text-classification", model="Hello-SimpleAI/chatgpt-detector-roberta")
text = "The Roman Empire was the post-Republican period of ancient Rome."
res = classifier(text)
print("WIKIPEDIA RESULT:", res)

text_ai = "Artificial intelligence is a transformative technology that reshapes how we interact with information."
res_ai = classifier(text_ai)
print("AI RESULT:", res_ai)
