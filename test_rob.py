from transformers import pipeline
pipe = pipeline("text-classification", model="roberta-base-openai-detector")
res = pipe("Artificial intelligence is transforming education by providing personalized learning experiences.")
print("PIPELINE RESULT:", res)
