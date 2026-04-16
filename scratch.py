from model.plagiarism_model import compute_plagiarism_score
from model.ai_detector import compute_ai_probability

p = "Artificial Intelligence is transforming education by providing personalized learning experiences. Furthermore, it enables predictive analytics for student performance."

print("Plag:", compute_plagiarism_score(p))
print("AI:", compute_ai_probability(p))
