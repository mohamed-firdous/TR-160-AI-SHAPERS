import sys
import os
sys.path.append(os.getcwd())
from model.analyze_document import analyze_document

def test_wikipedia():
    print("\n--- Testing Wikipedia Snippet ---")
    text = "The Roman Empire was the post-Republican period of ancient Rome. As a polity, it included large territorial holdings around the Mediterranean Sea in Europe, North Africa, and Western Asia, ruled by emperors. From the accession of Augustus as the first Roman emperor to the military anarchy of the third century, it was a principate with Italy as the metropole of its provinces and the city of Rome as its sole capital."
    # We need a file for analyze_document
    with open("wiki_test.txt", "w") as f:
        f.write(text * 5) # duplication to reach 120 words
    
    result = analyze_document("wiki_test.txt")
    print("Overall AI:", result.get("overall_ai_probability"))
    print("Overall Plag:", result.get("overall_plagiarism_score"))

def test_ai_generated():
    print("\n--- Testing AI Generated Essay ---")
    text = "Artificial intelligence is a transformative technology that reshapes how we interact with information. Furthermore, it provides unprecedented opportunities for personalized learning and data-driven decision making. In conclusion, the integration of AI into educational systems is not merely an option but a necessity for modern pedagogical success."
    with open("ai_test.txt", "w") as f:
        f.write(text * 5)
        
    result = analyze_document("ai_test.txt")
    print("Overall AI:", result.get("overall_ai_probability"))
    print("Overall Plag:", result.get("overall_plagiarism_score"))

if __name__ == "__main__":
    test_wikipedia()
    test_ai_generated()
