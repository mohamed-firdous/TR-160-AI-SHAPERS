import os
import json
from analyze_document import analyze_document

def run_test():

    test_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'sample_data', 
        'sample_assignment.pdf'
    ))
    
    print("[*] Commencing integrated AI testing framework.")
    print(f"[*] Targeting test file payload: {test_file}\n")
    print("[*] Instantiating Transformers, initializing NLP layers... (May take a few moments)\n")
    
    result = analyze_document(test_file)
    
    print("\n============== EVALUATION RESULTS ==============\n")
    print(json.dumps(result, indent=2))
    print("\n================================================")

if __name__ == "__main__":
    run_test()