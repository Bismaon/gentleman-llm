import os
from dotenv import load_dotenv
import requests

from util import write_functions_to_json

load_dotenv()


# upload a document (proof of concept)
filename = "exemple.py"
content='''
import os

def list_files(directory: str) -> list[str]:
    """Lists all files in a given directory.

    Args:
        directory (str): The name of the directory

    Returns:
        list[str]: Lists of all file names in a directory.
    """

    try:
        return [
            f
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
    except FileNotFoundError:
        print(f"Directory not found: {directory}")
        return []
    except Exception as e:
        print(f"Error listing files in {directory}: {e}")
        return []
'''
resp = requests.post(
    "http://127.0.0.1:8000/upload",
    json={
        "filepath": filename,
        "content": content,
    },
)

folder_name = resp.json()
print(f"Saved in folder: {folder_name}")

# analyze a document (proof of concept)
resp = requests.post(
    "http://127.0.0.1:8000/analyze",
    json={
        "filepath": f"{folder_name}/{filename}",
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "hf_token": os.getenv("HF_TOKEN"),
    },
)

write_functions_to_json(resp.json(), "exemple", dir=folder_name)


