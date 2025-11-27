from dotenv import load_dotenv
from gentleman_llm import GentlemanLLM
import os

if __name__ == "__main__":
    load_dotenv()
    service = GentlemanLLM(
        model="meta-llama/Llama-3.1-8B-Instruct",
        hf_token=os.getenv("HF_TOKEN")
    )
    result = service.analyze_file("C:/Github/gentleman-llm/documents/code/master.py")
    print(result)
