import asyncio
import sys
sys.path.append("/Users/sainithickroshaan/AI-Content-Detector")
from model.plagiarism_model import compute_plagiarism_score
from model.ai_detector import compute_ai_probability

async def test():
    txt = "Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy that, through cellular respiration, can later be released to fuel the organism's activities."
    print("AI PROBABILITY (Wikipedia Text):", compute_ai_probability(txt))
    print("PLAGIARISM SCORE (Wikipedia Text):", await compute_plagiarism_score(txt))

if __name__ == '__main__':
    asyncio.run(test())
