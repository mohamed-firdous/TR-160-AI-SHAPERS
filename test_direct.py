import sys
sys.path.append("/Users/sainithickroshaan/AI-Content-Detector")
from model.ai_detector import compute_ai_probability

p1 = "Artificial Intelligence is completely transforming the landscape of modern education by enabling automated systems to assist in grading, tutoring, and massive content generation."
print("P1 PROB:", compute_ai_probability(p1))

p2 = "Educational institutions must immediately adopt these technologies to securely ensure academic fairness and strict authenticity spanning modern boundaries."
print("P2 PROB:", compute_ai_probability(p2))
