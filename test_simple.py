from transformers import AutoConfig
config = AutoConfig.from_pretrained("Hello-SimpleAI/chatgpt-detector-roberta")
print(config.id2label)
