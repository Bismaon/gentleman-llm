import ast
import json
import os
import re

CONTAINERS = {"list", "dict", "tuple", "set", "frozenset"}

PRIMITIVES = {"int", "float", "bool", "str", "bytes", "none", "any", "object"} | CONTAINERS
CUSTOM = {"DB"}
NON_EXHAUSTIVE = {"date", "time", "datetime", "timedelta", "timezone","Path", "PurePath", "PathLike", "UUID", "Decimal", "Complex","Pattern", "Match", "Callable"}

def generate_valid_types(depth=2):
    """
    Generate an exhaustive set of type expressions up to a given nesting depth.
    """
    base = PRIMITIVES | CUSTOM 
    valid = set(base)

    def expand(base_types, current_depth):
        if current_depth > depth:
            return set()

        new_types = set()
        for outer in CONTAINERS:
            for inner in base_types:
                if outer == "dict":
                    for inner2 in base_types:
                        new_types.add(f"dict[{inner},{inner2}]")
                elif outer == "tuple":
                    for inner2 in base_types:
                        new_types.add(f"tuple[{inner},{inner2}]")
                else:
                    new_types.add(f"{outer}[{inner}]")

        if current_depth < depth:
            new_types |= expand(new_types, current_depth + 1)

        return new_types

    valid |= expand(base, 1)
    return valid
VALID_BASE_TYPES = generate_valid_types(depth=2) | CONTAINERS | NON_EXHAUSTIVE

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


def read_file(filepath: str) -> str:
    """
    Read and return the content of a file given its name and parent directory.

    Parameters
    ----------
    filepath : str
        The name of path of the file

    Returns
    -------
        str
            Content of the file
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return ""
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return ""


def write_file(filepath: str, content: str) -> str:
    """
    Write content to a file inside the given directory.

    Parameters
    ----------
        filepath : str
            Path to the file to create/overwrite.
        content : str
            The text content to write.

    Returns
    -------
        str
            Full path of the written file.
    """
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


def get_json(filename: str) -> dict:
    """
    Load and return the JSON from the `filename` file.

    Parameters
    ----------
        filename : str
            JSON filename.

    Returns
    -------
        dict
            The JSON.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"JSON file not found: {filename}")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON from file.")
        return {}
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return {}

def extract_functions(filepath:str)->list[dict]:
    code = read_file(filepath)
    tree = ast.parse(code, filename=filepath)

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_source = ast.get_source_segment(code, node)
            param_names = [param.arg for param in node.args.args]
            ast.get_source_segment(code, node)
            functions.append({
                "name": node.name,
                "parameters": param_names,
                "source": func_source,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                "types":[],
                "description":"",
                "tags":[],
            })
    return functions

def validate_types(llm_answer: str) -> list[str]|Exception:
    try:
        value = ast.literal_eval(llm_answer.strip())
        if not isinstance(value, list):
            raise ValueError("Expected a list of type names.")
        sanitized = []
        
        for v in value:
            try:
                t = sanitize_and_validate(v)
                sanitized.append(t)
            except Exception as s_v_e:
                raise s_v_e
        return sanitized 
    except Exception as e:
        print(f"Error validating types: {e}")
        return []

def sanitize_and_validate(t: str) -> str:
    if not isinstance(t, str):
        raise Exception(f"Type name must be a string.\n Type: {t}")

    # Remove  "x:int" or "x - str"
    if ":" in t:
        t = t.split(":")[-1].strip()
    elif "-" in t:
        parts = t.split("-")
        if len(parts[-1].strip()) > 0:
            t = parts[-1].strip()

    if any(item in t for item in ["(" ,")","[[", "{", "}"]):
        raise Exception(f"Invalid characters in type name.\n Type: {t}")
    
    # remove whitespace
    t = re.sub(r"\s+", "", t)

    if not is_valid_type(t):
        raise Exception(f"The given type is not a valid python type.\n Type: {t}")
    return t

def is_valid_type(expr: str) -> bool:
    return expr in VALID_BASE_TYPES 

def next_available_filename(base_name: str) -> str:
    """
    Given a base_name like 'filename_func_def',
    returns a file name like 'filename_func_def_1.txt'
    or increments until a free name is found.
    """
    i = 1
    while True:
        candidate = f"{base_name}_{i}.txt"
        if not os.path.exists(candidate):
            return candidate
        i += 1

def write_function_definitions(filepath: str, functions: list[dict]) -> None:
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    base_output_name = f"results/{base_name}_func_def"
    output_file = next_available_filename(base_output_name)

    with open(output_file, "w", encoding="utf-8") as f:
        for i, func in enumerate(functions, start=1):
            f.write(f"--- Function {i}: {func['name']} - {func["start_line"]}:{func["end_line"]}---")
            f.write(f"\n# Source:\n{func["source"]}")
            params = "("
            for param, p_type in zip(func['parameters'], func['types']):
                params += f"{param}: {p_type},"
            params+= ")"
            f.write(f"\n\n# Parameters:\n{params}")
            f.write(f"\n# Description:\n{func['description']}")
            f.write(f"\n# Tags:\n{', '.join(func['tags'])}")
            f.write("\n\n")

    print(f"Wrote {len(functions)} function definitions to {output_file}")
