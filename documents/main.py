from dotenv import load_dotenv
from util import write_functions_to_json
from gentleman_llm import GentlemanLLM
import os

if __name__ == "__main__":
    load_dotenv()
    service = GentlemanLLM(
        model="meta-llama/Llama-3.1-70B-Instruct",
        hf_token=os.getenv("HF_TOKEN")
    )
    result = service.analyze_file("./code/master.py")
    write_functions_to_json(result, "master.json")
