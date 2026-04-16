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


def compute_ai_probability(paragraph):
    """
    Computes a deeply robust weighted AI prediction integrating 5 separate cognitive and spatial maps.
    Weights: 30% PPL, 20% Variance, 15% Repetition, 15% Coherence, 20% Classifier.
    """
    if not paragraph.strip():
        return 0.0
        
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
            # AI has very low perplexity (10-25). Humans even in academic writing are 30-60+
            min_ppl = 15.0
            max_ppl = 60.0
            ppl_score = 1.0 - ((max(min_ppl, min(max_ppl, perplexity)) - min_ppl) / (max_ppl - min_ppl))
            
        # --- 2. Entropy Variance Score (10%) ---
        entropy_var = compute_entropy_variance(paragraph)
        entropy_score = 0.5
        if entropy_var > 0:
            # AI has extremely low variance (<2.5). Humans are usually >4.5
            if entropy_var < 2.5: entropy_score = 1.0
            elif entropy_var > 6.0: entropy_score = 0.0
            else: entropy_score = 1.0 - ((entropy_var - 2.5) / 3.5)

        sentences = [s.strip() for s in re.split(r'[.!?]+', paragraph) if len(s.strip()) > 3]
        
        # --- 3. Burstiness / Variance (8%) ---
        burstiness_score = 0.5
        if len(sentences) > 1:
            lengths = [len(s.split()) for s in sentences]
            try:
                variance = statistics.stdev(lengths)
                # Humans have high variance (longer and shorter sentences mixed). AI is very uniform.
                if variance < 4.0: burstiness_score = 1.0
                elif variance > 18.0: burstiness_score = 0.0
                else: burstiness_score = 1.0 - ((variance - 4.0) / 14.0)
            except Exception: pass

        # --- 4. Repetition Patterns (7%) ---
        words = [w.lower() for w in re.findall(r'\b\w+\b', paragraph)]
        repetition_score = 0.5
        if words:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.45: repetition_score = 1.0
            elif unique_ratio > 0.85: repetition_score = 0.0
            else: repetition_score = 1.0 - ((unique_ratio - 0.45) / 0.4)

        # --- 5. Semantic Coherence (10%) ---
        coherence_score = 0.5
        if sentence_model and len(sentences) > 1:
            embs = sentence_model.encode(sentences, convert_to_tensor=True)
            similarities = [util.cos_sim(embs[i], embs[i+1]).item() for i in range(len(embs)-1)]
            avg_coherence = sum(similarities) / len(similarities)
            # AI has extremely high coherence (>0.7). Humans are 0.3-0.5.
            if avg_coherence > 0.75: coherence_score = 1.0
            elif avg_coherence < 0.3: coherence_score = 0.0
            else: coherence_score = (avg_coherence - 0.3) / 0.45
            
        # --- 6. Transformer Classifier Model (40%) ---
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

        # === COMPOSITE NORMALIZATION ===
        final_probability = (
            (0.40 * classifier_probability) + 
            (0.25 * ppl_score) + 
            (0.10 * entropy_score) + 
            (0.10 * coherence_score) + 
            (0.08 * burstiness_score) + 
            (0.07 * repetition_score)
        )
        
        # --- HUMAN ACADEMIC CORRECTION ---
        # If the text shows high linguistic variance (low burstiness_score) 
        # or non-robotic flow (low coherence_score), it's likely a complex human write.
        if burstiness_score < 0.35 and coherence_score < 0.45:
            final_probability *= 0.5  # Heavy discount for complex human structure
        
        # Exponential Override rule: classifier > 0.85 AND ppl_score > 0.8
        if classifier_probability > 0.85 and ppl_score > 0.80:
            final_probability = max(final_probability, 0.92)
        elif classifier_probability < 0.25 and ppl_score < 0.25:
            final_probability = min(final_probability, 0.10)

        # FINAL CALIBRATION: More non-linear mapping to separate Human from AI
        if final_probability > 0.75:
            # High Risk AI (65-95)
            calibrated = 0.65 + (final_probability - 0.75) * (0.30 / 0.25)
        elif final_probability > 0.40:
            # Gray area / Mixed (35-65) - map 0.4-0.75 to 0.35-0.65
            calibrated = 0.35 + (final_probability - 0.4) * (0.30 / 0.35)
        else:
            # Human (10-35) - map 0.0-0.4 to 0.10-0.35
            calibrated = 0.10 + final_probability * (0.25 / 0.4)

        return round(float(calibrated), 2)
    except Exception as e:
        print(f"Error computing AI multivariable framework: {e}")
        return 0.0
