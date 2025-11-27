import os
from dotenv import load_dotenv
import requests

from util import write_functions_to_json

load_dotenv()
resp = requests.post(
    "http://127.0.0.1:8000/analyze",
    json={
        "filepath": "code/master.py",
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "hf_token": os.getenv("HF_TOKEN"),
    },
)

write_functions_to_json(resp.json(), "test_api")
