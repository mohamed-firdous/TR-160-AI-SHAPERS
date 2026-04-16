import asyncio
import time
import os
import sys

# Add root to path for imports
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from model.analyze_document import analyze_document

# TEST SAMPLES
GPT4_ESSAY = """
The exploration of Mars represents one of the most ambitious and transformative goals in modern space science. As the most Earth-like planet in our solar system, Mars offers a unique opportunity to search for signs of past microbial life and understand the evolution of planetary habitability. Sending humans to the Red Planet would require overcoming significant technological hurdles, including propulsion systems capable of faster transit times, life-support hardware that can operate for years without maintenance, and shielding to protect astronauts from hazardous cosmic radiation. Beyond the technical challenges, the colonization of Mars raises profound ethical and philosophical questions about our role as a multi-planetary species. Establishing a permanent human presence on another world would not only safeguard humanity's future against terrestrial catastrophes but also inspire a new generation of scientists and explorers to push the boundaries of what is possible. It is a journey that demands international cooperation and a shared vision for the future of our civilization.
"""

WIKIPEDIA_PARA = """
The Industrial Revolution was a period of global economic transition towards more efficient and stable manufacturing processes that succeeded the Agricultural Revolution. This transition included going from hand production methods to machines, new chemical manufacturing and iron production processes, the increasing use of steam power and water power, the development of machine tools and the rise of the mechanized factory system. The Industrial Revolution also led to an unprecedented rise in the rate of population growth. Textiles were the dominant industry of the Industrial Revolution in terms of employment, value of output and capital invested. The textile industry was also the first to use modern production methods. The Industrial Revolution began in Great Britain, and many of the technological and architectural innovations were of British origin. By the mid-18th century, Britain was the world's leading commercial nation, controlling a global trading empire with colonies in North America and the Caribbean.
"""

HUMAN_ESSAY = """
The possibility of extraterrestrial life has fascinated humans for centuries, sparking countless debates among scientists and philosophers alike. Recent discoveries by the Kepler space telescope suggest that our galaxy may contain millions of Earth-like planets, many of which reside in the 'habitable zone' where liquid water could exist. This realization brings us closer to answering one of humanity's most profound questions: Are we alone in the universe? While we have yet to find direct evidence of microbial life on Mars or elsewhere, the mission to explore these worlds continues to drive technological innovation on Earth. Interplanetary travel presents monumental challenges, from the physiological effects of long-term microgravity to the psychological isolation of a three-year round trip. However, the potential rewards for our species are immense, potentially providing a secondary home for humanity and a deeper understanding of our origins as a biological consequence of cosmic evolution.
"""

async def run_test(name, text):
    temp_file = f"test_{name}.txt"
    with open(temp_file, "w") as f:
        f.write(text)
    
    start = time.time()
    result = await analyze_document(temp_file)
    end = time.time()
    
    os.remove(temp_file)
    return result, end - start

async def main():
    print("=== AI DETECTION ACCURACY BENCHMARK ===")
    
    tests = [
        ("GPT4_AI", GPT4_ESSAY),
        ("WIKIPEDIA", WIKIPEDIA_PARA),
        ("HUMAN", HUMAN_ESSAY)
    ]
    
    for name, text in tests:
        print(f"\n>>> TESTING: {name}")
        res, duration = await run_test(name, text)
        
        ai_risk = res['overall_ai_probability']
        plag_score = res['overall_plagiarism_score']
        
        print(f"AI Risk: {ai_risk}%")
        print(f"Plagiarism: {plag_score}%")
        print(f"Latency: {duration:.2f}s")
        
        # Validation Logic (Updated for new requirements)
        if name == "GPT4_AI":
            if 70 <= ai_risk <= 98: print("✅ PASS: AI text detected correctly.")
            else: print(f"❌ FAIL: AI text risk {ai_risk}% out of range (70-98%)")
        elif name == "WIKIPEDIA":
            if 10 <= ai_risk <= 35: print("✅ PASS: Wiki text detected as human benchmark.")
            else: print(f"❌ FAIL: Wiki text risk {ai_risk}% out of range.")
        elif name == "HUMAN":
            if 10 <= ai_risk <= 35: print("✅ PASS: Human text detected correctly.")
            else: print(f"❌ FAIL: Human text risk {ai_risk}% out of range.")

if __name__ == "__main__":
    asyncio.run(main())
