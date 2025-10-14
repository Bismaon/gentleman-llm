import os
from openai import OpenAI
from dotenv import load_dotenv
from util import get_json, list_files, read_file, write_file
from local import (
    THINKING_STEPS,
    PERSONA,
    DEPTHS,
    RULES,
)
import json
import ast

models = [
    "moonshotai/Kimi-K2-Instruct-0905",
    "deepseek-ai/DeepSeek-V3.1",
    "meta-llama/Llama-3.1-8B-Instruct",
]


def extract_defined_functions(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
    return functions

def analyze_file_with_llm(
    filepath: str,
    schema_dict: dict,
    d_i: int = 0, 
    function_types_guide: str = "",
    model: str = "meta-llama/Llama-3.1-8B-Instruct",
) -> str:
    """
    Reads a file and sends its content to the LLM for analysis.

    Parameters
    ----------
        filepath : str
            Path to the file tp analyze.
        model : str
            Model to use (default:  Llama 3.1 8B Instruct).

    Returns
    -------
    str
        The LLM response text.
    """
    depth_index = d_i
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        functions = extract_defined_functions(filepath)
        print(f"Functions found in {filepath}: {functions}")
    except FileNotFoundError:
        return f"File not found: {filepath}"
    except Exception as e:
        return f"Error reading file {filepath}: {e}"
    pass
    concept_res = get_concept(schema_dict, model, depth_index, function_types_guide, content, functions)
    # projection_res = get_projection()
    return concept_res.choices[0].message.content

def get_concept(schema_dict, model, depth_index, function_types_guide, content, functions):
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": PERSONA},
            {"role": "system", "content": RULES},
            {"role": "system", "content": THINKING_STEPS},
            {"role": "system", "content": function_types_guide},
            {"role": "user", "content": DEPTHS[depth_index]},
            {
                "role": "user",
                "content": f"Classify every function {functions} listed in this file:\n\n{content}",
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "ConceptModel", "schema": schema_dict},
        },
    )
    



if __name__ == "__main__":
    load_dotenv()

    model_in_use = models[2]
    d_i = 0  # depth index
    concept_schema = get_json("formats/concept_format.json")
    # projection_schema = get_json("formats/projection_format.json")
    function_types = get_json("formats/function_types_guide.json")
    function_types_guide = json.dumps(function_types, indent=4)

    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.getenv("HF_TOKEN"),
    )

    list_of_files = list_files("code")
    for file in list_of_files:
        content = read_file(f"code/{file}")
        print(f"--- {file} ---")
        print()

    for i in range (3):
        
        print(f"Analyzing file: {list_of_files[2]} with model {model_in_use} at depth {i}")
        response = analyze_file_with_llm(
            f"code/{list_of_files[2]}", concept_schema, d_i=i, model=model_in_use, function_types_guide=function_types_guide
        )
        write_file( f"results/analysis_{list_of_files[2]}_depth_{i}.json", response)
