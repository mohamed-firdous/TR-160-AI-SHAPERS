import torch
import re
import statistics
from transformers import GPT2LMHeadModel, GPT2TokenizerFast, pipeline
from sentence_transformers import SentenceTransformer, util

device = "cuda" if torch.cuda.is_available() else "cpu"

try:
    # Shifted to base GPT2! 
    # GPT2-Large on Mac CPUs causes extreme memory blocking/timeout failures mid-inference.
    gpt_model_id = "gpt2"
    gpt_model = GPT2LMHeadModel.from_pretrained(gpt_model_id).to(device)
    gpt_tokenizer = GPT2TokenizerFast.from_pretrained(gpt_model_id)
except Exception as e:
    print(f"Warning: Could not load GPT2 model. {e}")
    gpt_model = None
    gpt_tokenizer = None

try:
    classifier_pipeline = pipeline("text-classification", model="Hello-SimpleAI/chatgpt-detector-roberta", device=0 if device == "cuda" else -1)
except Exception as e:
    print(f"Warning: Could not load text-classifier pipeline. {e}")
    classifier_pipeline = None

try:
    sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Warning: Could not load MiniLM. {e}")
    sentence_model = None



def compute_entropy_variance(text):
    """
    Calculate the variance of token probability entropy across the text.
    AI text tends to be more consistent (lower entropy variance).
    """
    if not gpt_tokenizer or not gpt_model or not text.strip():
        return 0.0
        
    try:
        encodings = gpt_tokenizer(text, return_tensors='pt')
        input_ids = encodings.input_ids.to(device)
        
        if input_ids.size(1) < 2:
            return 0.0

        with torch.no_grad():
            outputs = gpt_model(input_ids)
            logits = outputs.logits  # shape [1, seq_len, vocab_size]

        # Logits at position i predict token at i+1
        # probs[0, i, :] is distribution for next token
        probs = torch.softmax(logits[:, :-1, :], dim=-1)
        # H = -sum(p * log(p))
        token_entropies = -torch.sum(probs * torch.log(probs + 1e-12), dim=-1)
        
        variance = torch.var(token_entropies).item()
        return variance
    except Exception:
        return 0.0


async def compute_ai_probability(paragraph):
    """
    Computes a deeply robust weighted AI prediction integrating 6 separate signals.
    Refactored to be ASYNC for high-performance orchestration.
    """
    if not paragraph.strip():
        return 0.0
        
    def _sync_inference():
        try:
            # --- 1. Perplexity Score (25%) ---
            perplexity = 0.0
            encodings = gpt_tokenizer(paragraph, return_tensors='pt')
            input_ids = encodings.input_ids.to(device)
            if input_ids.size(1) > 1:
                with torch.no_grad():
                    outputs = gpt_model(input_ids, labels=input_ids)
                    loss = outputs.loss
                    perplexity = torch.exp(loss).item()
            
            ppl_score = 0.5
            if perplexity > 0:
                min_ppl = 15.0
                max_ppl = 60.0
                ppl_score = 1.0 - ((max(min_ppl, min(max_ppl, perplexity)) - min_ppl) / (max_ppl - min_ppl))
                
            # --- 2. Entropy Variance Score (15%) ---
            entropy_var = compute_entropy_variance(paragraph)
            entropy_score = 0.5
            if entropy_var > 0:
                if entropy_var < 2.5: entropy_score = 1.0
                elif entropy_var > 6.0: entropy_score = 0.0
                else: entropy_score = 1.0 - ((entropy_var - 2.5) / 3.5)

            sentences = [s.strip() for s in re.split(r'[.!?]+', paragraph) if len(s.strip()) > 3]
            
            # --- 3. Burstiness / Variance (5%) ---
            burstiness_score = 0.5
            if len(sentences) > 1:
                lengths = [len(s.split()) for s in sentences]
                try:
                    variance = statistics.stdev(lengths)
                    if variance < 4.0: burstiness_score = 1.0
                    elif variance > 18.0: burstiness_score = 0.0
                    else: burstiness_score = 1.0 - ((variance - 4.0) / 14.0)
                except Exception: pass

            # --- 4. Repetition Patterns (5%) ---
            words = [w.lower() for w in re.findall(r'\b\w+\b', paragraph)]
            repetition_score = 0.5
            if words:
                unique_ratio = len(set(words)) / len(words)
                if unique_ratio < 0.45: repetition_score = 1.0
                elif unique_ratio > 0.85: repetition_score = 0.0
                else: repetition_score = 1.0 - ((unique_ratio - 0.45) / 0.4)

            # --- 5. Semantic Coherence (5%) ---
            coherence_score = 0.5
            if sentence_model and len(sentences) > 1:
                embs = sentence_model.encode(sentences, convert_to_tensor=True)
                similarities = [util.cos_sim(embs[i], embs[i+1]).item() for i in range(len(embs)-1)]
                avg_coherence = sum(similarities) / len(similarities)
                if avg_coherence > 0.75: coherence_score = 1.0
                elif avg_coherence < 0.3: coherence_score = 0.0
                else: coherence_score = (avg_coherence - 0.3) / 0.45
                
            # --- 6. Transformer Classifier Model (45%) ---
            classifier_probability = 0.5
            if classifier_pipeline:
                try:
                    result = classifier_pipeline(paragraph[:2000])[0]
                    label_val = str(result['label']).lower()
                    if 'fake' in label_val or 'chatgpt' in label_val or '1' in label_val:
                        classifier_probability = result['score']
                    else:
                        classifier_probability = 1.0 - result['score']
                except Exception: pass

            # === COMPOSITE NORMALIZATION (GPT-4 / GPT-4o ENHANCED) ===
            # Re-weighted ensemble where Classifier is dominant
            final_probability = (
                (0.60 * classifier_probability) + 
                (0.20 * ppl_score) + 
                (0.10 * entropy_score) + 
                (0.05 * coherence_score) + 
                (0.03 * burstiness_score) + 
                (0.02 * repetition_score)
            )

            # FINAL CALIBRATION SCALING (Requirement 4 - Refined for Hallmarks)
            # human benchmark (Wiki/Student): 10-35%
            # GPT-4 generated: 70-95%
            if final_probability > 0.75:
                # AI BRACKET: Map [0.75, 1.0] -> [70, 95]
                calibrated = 70.0 + (final_probability - 0.75) * (25.0 / 0.25)
            elif final_probability > 0.55:
                # UNCERTAIN BRACKET: Map [0.55, 0.75] -> [35, 70]
                calibrated = 35.0 + (final_probability - 0.55) * (35.0 / 0.20)
            else:
                # HUMAN BRACKET: Map [0, 0.55] -> [10, 35]
                calibrated = 10.0 + final_probability * (25.0 / 0.55)

            return round(float(calibrated), 1)
        except Exception as e:
            print(f"Error computing AI multivariable framework: {e}")
            return 0.0

    # Offload to thread to keep async executor free
    import asyncio
    return await asyncio.to_thread(_sync_inference)
