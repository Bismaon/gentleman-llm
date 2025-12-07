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
    names = ["master","__init__", "annuaire_parser","repertoire_parser","schedule_parser","udem_info_parser","xlsx2csv"] 
    for name in names:
        result = service.analyze_file(f"./code/{name}.py")
        write_functions_to_json(result, f"{name}.json")
