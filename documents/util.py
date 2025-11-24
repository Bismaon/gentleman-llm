import ast
import json
import os
import re
import time
import logging

CONTAINERS = {"list", "dict", "tuple", "set", "frozenset"}

PRIMITIVES = {"int", "float", "bool", "str", "bytes", "none", "any", "object"} | CONTAINERS
CUSTOM = {"DB"}
NON_EXHAUSTIVE = {"date", "time", "datetime", "timedelta", "timezone","Path", "PurePath", "PathLike", "UUID", "Decimal", "Complex","Pattern", "Match", "Callable"}

logging.basicConfig(
    filename="timing.log",          # or any file path you want
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def generate_valid_types(depth=1):
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
                if outer == "dict" or outer == "tuple":
                    for inner2 in base_types:
                        new_types.add(f"{outer}[{inner},{inner2}]")
                else:
                    new_types.add(f"{outer}[{inner}]")

        if current_depth < depth:
            new_types |= expand(new_types, current_depth + 1)

        return new_types

    valid |= expand(base, 1)
    return valid

def write_valid_types(plus, file:str, output_path="results/valid_types"):
    """
    Writes all valid types (VALID_BASE_TYPES) to a file, sorted alphabetically.
    """
    try:
        out = next_available_filename(f"{output_path}_{file}")
        with open(out, "w", encoding="utf-8") as f:
            for t in list(VALID_BASE_TYPES):
                f.write(f"{t}\n")
            for t in list(plus):
                f.write(f"{t}\n")
        print(f"[OK] Valid types written to {out}")
    except Exception as e:
        print(f"[ERROR] Cannot write valid types: {e}")
        
VALID_BASE_TYPES = PRIMITIVES | NON_EXHAUSTIVE | generate_valid_types()

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

def next_available_filename(base_name: str, ext:str="txt") -> str:
    """
    Given a base_name like 'filename_func_def',
    returns a file name like 'filename_func_def_1.txt'
    or increments until a free name is found.
    """
    directory = os.path.dirname(base_name) or "."
    filename_root = os.path.basename(base_name)

    pattern = re.compile(rf"^{re.escape(filename_root)}_(\d+)\.{ext}$")

    existing_versions = []

    for file in os.listdir(directory):
        match = pattern.match(file)
        if match:
            version = int(match.group(1))
            existing_versions.append(version)

    next_version = max(existing_versions, default=0) + 1

    return os.path.join(directory, f"{filename_root}_{next_version}.{ext}")

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

def list_imports(node, imports: list[str]):
    if isinstance(node, ast.Import):
        for alias in node.names:
            sanitized_name = sanitize(alias.name)
            imports.append(sanitized_name)

    elif isinstance(node, ast.ImportFrom):
        for alias in node.names:
            sanitized_name = sanitize(alias.name)
            imports.append(sanitized_name)

def list_functions(code, functions, node):
    if isinstance(node, ast.FunctionDef):
        func_source = ast.get_source_segment(code, node)
        param_names = [param.arg for param in node.args.args]

        functions.append({
            "name": node.name,
            "parameters": [(param, "") for param in param_names],
            "source": func_source,
            "start_line": node.lineno,
            "end_line": node.end_lineno,
            "called_by": [],
            "calls": [],
            "description": "",
            "tags": [],
            "category": "",
            "return": ("","")
        })

def list_calls(tree, functions):
    local_function_names = {f["name"] for f in functions}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            index = index_of(functions, "name", func_name)
            calls = set()

            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    if isinstance(inner.func, ast.Name):
                        name = inner.func.id
                        if name in local_function_names:
                            calls.add(name)

                    elif isinstance(inner.func, ast.Attribute):
                        name = inner.func.attr
                        if name in local_function_names:
                            calls.add(name)

            functions[index]["calls"] = list(calls)

    return functions

def list_called_by(functions):
    for f in functions:
        caller = f["name"]

        for callee in f["calls"]:
            idx = index_of(functions, "name", callee)
            if idx != -1:
                functions[idx]["called_by"].append(caller)

    for f in functions:
        f["calls"] = sorted(set(f["calls"]))
        f["called_by"] = sorted(set(f["called_by"]))

    return functions

def list_returns(node, current_function, functions):
    if current_function is None:
        return

    index = index_of(functions, "name", current_function)
    
    if isinstance(node, ast.Return):
        value = node.value

        try:
            return_expr = ast.unparse(value)
        except Exception:
            return_expr = "Unknown"

        inferred_type = infer_python_type_from_ast(value)

        functions[index]["return"] = (return_expr, inferred_type )

def extract_information(filepath: str) -> tuple[list[dict], set[str]]:
    code = read_file(filepath)
    tree = ast.parse(code, filepath)

    functions = []
    imports = []
    current_function = None

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            current_function = node.name
        list_functions(code, functions, node)
        list_imports(node, imports)
        list_returns(node, current_function, functions)

    functions = list_calls(tree, functions)
    functions = list_called_by(functions)

    return functions, set(imports)

def validate_types(llm_answer: str, imports: set[str]) -> list[str]|Exception:
    try:
        value = ast.literal_eval(llm_answer.strip())
    except Exception as e:
        raise ValueError(f"Invalid Python literal for type list: {e}") from e

    if not isinstance(value, list):
        raise ValueError(f"Expected a list of type names, got {type(value).__name__}")

    sanitized = []
    for v in value:
        try:
            t = sanitize_and_validate(v, imports)
            sanitized.append(t)
        except Exception as e:
            raise ValueError(f"Invalid type entry '{v}': {e}") from e

    return sanitized

def validate_type(llm_answer: str, imports: set[str]) -> str|Exception:
    if not isinstance(llm_answer, str):
        raise ValueError(f"Expected a list of type names, got {type(llm_answer).__name__}")

    sanitized = ''
    try:
        sanitized = sanitize_and_validate(llm_answer, imports)
    except Exception as e:
        raise ValueError(f"Invalid type entry '{llm_answer}': {e}") from e

    return sanitized

def sanitize_and_validate(t: str, imports: set[str]) -> str:
    sanitized_t = sanitize(t)

    if not is_valid_type(sanitized_t, imports):
        raise ValueError(f"Unknown or unsupported type name: '{sanitized_t}'")
    
    return sanitized_t

def sanitize(t):
    if not isinstance(t, str):
        raise TypeError(f"Type name must be a string.\n Type: {t}")

    # Remove  "x:int" or "x - str"
    if ":" in t:
        t = t.split(":")[-1].strip()
    elif "-" in t:
        parts = t.split("-")
        if len(parts[-1].strip()) > 0:
            t = parts[-1].strip()
    t = re.sub(r"\s+", "", t)
    match = re.match(r"^(\w+)", t.strip().lower()) # get root type

    if match:
        t = match.group(1)

    if any(ch in t for ch in ["(" ,")","[[", "{", "}"]):
        raise ValueError(f"Invalid characters in type name: '{t}'")
    return t

def is_valid_type(expr: str, imports:set[str]) -> bool:
    return expr in (VALID_BASE_TYPES|imports) 

def validate_tags(llm_answer: str) -> list[str]|Exception:
    try:
        value = ast.literal_eval(llm_answer.strip())
    except Exception as e:
        raise ValueError(f"Invalid Python literal for tags list: {e}") from e
    if not isinstance(value, list):
        raise ValueError("Expected a list of tags string.")
    if not all(isinstance(tag, str) for tag in value):
        raise ValueError("All tags must be strings.")
        
    return value 

def valid_category(answer_LLM:str, function_types):
    ans = answer_LLM.strip()
    ans = ans.replace('"','').replace("'","")
    if not in_list(ans, function_types):
        raise ValueError(f"Invalid category: {ans}")
    else:
        return True

def in_range(value:int, min_val:int, max_val:int)->bool:
    return min_val <= value <= max_val

def index_of(dicts:list[dict], key:str, value:any):
    for i, d in enumerate(dicts):
        if d.get(key) == value:
            return i
    return -1  # or None

def in_list(value,list_str):
    low_val = value.lower()
    for items in list_str:
        if (items.lower() == low_val):
            return True

    return False

def time_step(label: str, func, *args, **kwargs):
    start = time.perf_counter()
    try:
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"[TIME] {label}: {end - start:.3f} seconds")
        return result
    except Exception as e:
        end = time.perf_counter()
        logger.error(
            f"[TIME ERROR] {label} failed after {end - start:.3f} seconds "
            f"with exception: {e}"
        )
        raise

def write_function_definitions(filepath: str, functions: list[dict]) -> None:
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    base_output_name = f"results/{base_name}_func_def"
    output_file = next_available_filename(base_output_name)

    with open(output_file, "w", encoding="utf-8") as f:
        for i, func in enumerate(functions, start=1):
            f.write(f"--- Function {i}: {func['name']} - {func["start_line"]}:{func["end_line"]}---")
            f.write(f"\n# Source:\n{func["source"]}")
            params = "("
            for param, p_type in func["parameters"]:
                params += f"{param}: {p_type},"
            params+= ")"
            f.write(f"\n\n# Parameters:\n{params}")
            return_value, return_type = func["return"]

            f.write(f"\n# Returns:\n{return_value}:{return_type}")
            f.write(f"\n# Category:\n{func['category']}")
            f.write(f"\n# Description:\n{func['description']}")
            f.write(f"\n# Tags:\n{', '.join(func['tags'])}")
            f.write(f"\n# Calls:\n{', '.join(func['calls'])}")
            f.write(f"\n# Called by:\n{', '.join(func['called_by'])}")
            f.write("\n\n")

    print(f"Wrote {len(functions)} function definitions to {output_file}")

def write_functions_to_json(functions: list[dict], output:str):
    try:
        base_name = os.path.basename(output)
        base_name_no_ext = os.path.splitext(base_name)[0]
        base_output_name = f"results/{base_name_no_ext}_func_concepts"
        output_file = next_available_filename(base_output_name, ext="json")
        func_with_file = [{"file":base_name}] + functions
        with open(output_file, "w", encoding="utf-8") as out:
            json.dump(func_with_file, out, indent=4, ensure_ascii=False)

        print(f"[OK] JSON written: {output_file}")
        return output_file

    except Exception as e:
        print(f"[ERROR] Failed to write JSON: {e}")
        return ""

def infer_python_type_from_ast(node) -> str:
    if isinstance(node, ast.Tuple):
        return "tuple"

    if isinstance(node, ast.List):
        return "list"

    if isinstance(node, ast.Dict):
        return "dict"

    if isinstance(node, ast.Set):
        return "set"

    if isinstance(node, ast.Constant):
        # True, 5, "hi", None
        if isinstance(node.value, bool):
            return "bool"
        if isinstance(node.value, int):
            return "int"
        if isinstance(node.value, float):
            return "float"
        if isinstance(node.value, str):
            return "str"
        if node.value is None:
            return "None"
        return "any"

    if isinstance(node, ast.Name):
        # something like "return x"
        return "any"

    if isinstance(node, ast.Call):
        # return something() → unknown
        return "any"

    return "any"
