import os
from openai import OpenAI
from dotenv import load_dotenv
from local import FUNCTION_TYPES_GUIDE_WEB, THINKING_STEPS, FUNCTION_TYPES_GUIDE_BASE, PERSONA, DEPTHS, RULES, DEFINITIONS
import json
import ast

def list_files(directory: str) -> list[str]:
    """
    Lists all files in a given directory.

    Parameters
    ----------
    directory : str
        The name of the directory

    Returns
    -------
        list[str]
            Lists of all file names in a directory.
    """
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except FileNotFoundError:
        print(f"Directory not found: {directory}")
        return []
    except Exception as e:
        print(f"Error listing files in {directory}: {e}")
        return []

def read_file(directory: str, filename: str) -> str:
    """
    Read and return the content of a file given its name and parent directory.

    Parameters
    ----------
    directory : str
        The name of the directory
    filename : str
        The name of the file

    Returns
    -------
        str
            Content of the file
    """
    filepath = os.path.join(directory, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return ""
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return ""
    
def write_file(directory: str, filename: str, content: str) -> str:
    """
    Write content to a file inside the given directory.

    Parameters
    ----------
        directory : str
            Path to the directory.
        filename : str
            Name of the file to create/overwrite.
        content : str
            The text content to write.

    Returns
    -------
        str
            Full path of the written file.
    """
    os.makedirs(directory, exist_ok=True)  # ensure directory exists
    filepath = os.path.join(directory, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return ""
    except Exception as e:
        print(f"Error writing file {filepath}: {e}")
        return ""

def get_schema(filename:str) -> dict:
    """
    Load and return the JSON schema from the `filename` file.

    Parameters
    ----------
        filename : str
            JSON schema filename.

    Returns
    -------
        dict
            The JSON schema.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Schema file not found: {filename}")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON from schema file.")
        return {}
    except Exception as e:
        print(f"Error loading schema: {e}")
        return {}

def extract_defined_functions(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
    return functions

def extract_function_source(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=filepath)

    functions = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno - 1
            end_line = node.end_lineno
            func_source = "\n".join(source.splitlines()[start_line:end_line])
            functions[node.name] = func_source
    return functions


def analyze_file_with_llm(directory: str, filename: str, schema_dict:dict, d_i:int =0, model: str = "meta-llama/Llama-3.1-8B-Instruct") -> str:
    """
    Reads a file and sends its content to the LLM for analysis.
    
    Parameters
    ----------
        directory : str
            Path to the directory containing the file.
        filename : str
            Name of the file to analyze.
        model : str
            Model to use (default:  Llama 3.1 8B Instruct).
    
    Returns
    -------
    str 
        The LLM response text.
    """
    depth_index = d_i
    FUNCTION_TYPES_GUIDE = FUNCTION_TYPES_GUIDE_BASE + FUNCTION_TYPES_GUIDE_WEB
    filepath = os.path.join(directory, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        functions = extract_defined_functions(filepath)
        print(f"Functions found in {filename}: {functions}")
    except FileNotFoundError:
        return f"File not found: {filepath}"
    except Exception as e:
        return f"Error reading file {filepath}: {e}"
    pass
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": PERSONA},
            {"role": "system", "content": RULES},
            {"role": "system", "content": DEFINITIONS},
            {"role": "system", "content": THINKING_STEPS},
            {"role": "user", "content": DEPTHS[depth_index]},
            {"role": "user", "content": FUNCTION_TYPES_GUIDE},
            {"role": "user", "content": f"Classify every function {functions} listed in this file:\n\n{content}"}
        ],
        response_format={ "type": "json_schema", "json_schema": {
        "name": "ConceptModel",
        "schema":schema_dict }}
    )

    return response.choices[0].message.content


load_dotenv()

models = ["moonshotai/Kimi-K2-Instruct-0905", "deepseek-ai/DeepSeek-V3.1", "meta-llama/Llama-3.1-8B-Instruct"]
model_in_use = models[2]
simplified_schema = get_schema("simplified_format.json")

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_TOKEN"),
)

list_of_files = list_files("code")
for file in list_of_files:
    content = read_file("code", file)
    print(f"--- {file} ---")
    print()

response = analyze_file_with_llm("code", list_of_files[2], simplified_schema, d_i=2, model=model_in_use)

write_file("results", f"analysis_{list_of_files[2]}.json", response)

