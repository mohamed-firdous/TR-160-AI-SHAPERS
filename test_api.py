import requests
import json

url = "http://127.0.0.1:8000/upload"
filepath = "/Users/sainithickroshaan/AI-Content-Detector/sample_data/reference_articles/article1.txt"

files = {'file': open(filepath, 'rb')}
try:
    response = requests.post(url, files=files)
    print("STATUS:", response.status_code)
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("FAILED:", e)
