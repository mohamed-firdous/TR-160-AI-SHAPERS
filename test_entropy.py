import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

model_id = "gpt2"
tokenizer = GPT2TokenizerFast.from_pretrained(model_id)
model = GPT2LMHeadModel.from_pretrained(model_id)

text = "Artificial intelligence is a branch of computer science that aims to create intelligent machines."
encodings = tokenizer(text, return_tensors='pt')
input_ids = encodings.input_ids

with torch.no_grad():
    outputs = model(input_ids)
    logits = outputs.logits  # shape [1, seq_len, vocab_size]

# Shift logits and targets
# probabilities for each token given previous tokens
probs = torch.softmax(logits, dim=-1)
# Entropy at each position: -sum(p * log(p))
# But wait, the standard "predictability" entropy is for the NEXT token distribution.
# For each position i, probs[0, i, :] is the distribution of the NEXT token.
token_entropies = -torch.sum(probs * torch.log(probs + 1e-12), dim=-1) # shape [1, seq_len]

print("Token Entropies:", token_entropies[0].tolist())
print("Entropy Variance:", torch.var(token_entropies).item())
