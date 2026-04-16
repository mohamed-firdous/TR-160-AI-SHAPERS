import sys
sys.path.append("/Users/sainithickroshaan/AI-Content-Detector")
from model.ai_detector import compute_ai_probability

txt = "Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy that, through cellular respiration, can later be released to fuel the organism's activities."
print("AI PROBABILITY:", compute_ai_probability(txt))
