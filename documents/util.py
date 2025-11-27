import ast
import os
import re
import json

CONTAINERS = {"list", "dict", "tuple", "set"}

PRIMITIVES = {
    "int",
    "float",
    "bool",
    "str",
    "bytes",
    "none",
    "any",
    "object",
} | CONTAINERS
CUSTOM = {"DB"}
NON_EXHAUSTIVE = {
    "date",
    "time",
    "datetime",
    "timedelta",
    "timezone",
    "Path",
    "PurePath",
    "PathLike",
    "UUID",
    "Decimal",
    "Complex",
    "Pattern",
    "Match",
    "Callable",
}


def generate_valid_types(depth: int = 0) -> set[str]:
    """Generate an exhaustive set of type expressions up to a given nesting depth.

    Args:
        depth (int, optional): The depth of valid types to generate (d=0: list,dict; d=1: list[str], dict[str];...). Defaults to 0.

    Returns:
        set(str): The set of types to compare to for the LLM's answer.
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


VALID_BASE_TYPES = PRIMITIVES | NON_EXHAUSTIVE | generate_valid_types(0)


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


def read_file(filepath: str) -> str:
    """Read and return the content of a file given its name and parent directory.

    Args:
        filepath (str): The name of path of the file

    Returns:
        str: Content of the file
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


def next_available_filename(base_name: str, ext: str = "txt") -> str:
    """Given a base_name like 'filename_func_def', returns a file name like 'filename_func_def_1.txt' or increments until a free name is found.

    Args:
        base_name (str): The name of the file
        ext (str, optional): The extension of the file. Defaults to "txt".

    Returns:
        str: The name of the file numbered.
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


def list_imports(node: ast, imports: list[str]):
    """Lists the imports of the file.

    Args:
        node (ast): The current node explored by AST of the file.
        imports (list[str]): The list to add the imports to.
    """
    if isinstance(node, ast.Import):
        for alias in node.names:
            sanitized_name = sanitize(alias.name)
            imports.append(sanitized_name)

    elif isinstance(node, ast.ImportFrom):
        for alias in node.names:
            sanitized_name = sanitize(alias.name)
            imports.append(sanitized_name)


def list_functions(content: str, functions: list[dict], node: ast):
    """Appends the function in the file as a dict to the given functions' list.

    Args:
        code (str): The content of the file.
        functions (list[dict]): The lists to which all the functions dict will be added.
        node (ast): The current node being explored.
    """
    if isinstance(node, ast.FunctionDef):
        func_source = ast.get_source_segment(content, node)
        param_names = [param.arg for param in node.args.args]

        functions.append(
            {
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
                "return": ("", ""),
            }
        )


def list_calls(tree: ast.Module, functions: list[dict]) -> list[dict]:
    """Gets the calls made by each function in the file.

    Args:
        tree (ast.Module): The AST tree of the file.
        functions (list[dict]): The list of function dictionaries.

    Returns:
        list[dict]: The updated list of function dictionaries with call information.
    """

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


def list_called_by(functions: list[dict]) -> list[dict]:
    """Lists the functions that call each function in the file.

    Args:
        functions (list[dict]): The list of function dictionaries.

    Returns:
        list[dict]: The updated list of function dictionaries with caller information.
    """
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


def list_returns(node: ast, current_function: dict, functions: list[dict]):
    """Lists the return statements and their inferred types for the current function.

    Args:
        node (ast): The current AST node being explored.
        current_function (dict): The dictionary representing the current function.
        functions (list[dict]): The list of function dictionaries.
    """
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

        functions[index]["return"] = (return_expr, inferred_type)


def extract_information(filepath: str) -> tuple[list[dict], set[str]]:
    """Extracts information about functions and imports from a Python file.

    Args:
        filepath (str): The path to the Python file.

    Returns:
        tuple[list[dict], set[str]]: A tuple containing a list of function dictionaries and a set of import statements.
    """
    content = read_file(filepath)
    tree = ast.parse(content, filepath)

    functions = []
    imports = []
    current_function = None

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            current_function = node.name
        list_functions(content, functions, node)
        list_imports(node, imports)
        list_returns(node, current_function, functions)

    functions = list_calls(tree, functions)
    functions = list_called_by(functions)

    return functions, set(imports), content


def validate_types(llm_answer: str, imports: set[str]) -> list[str] | Exception:
    """Validates a list of types provided by the LLM answer.

    Args:
        llm_answer (str): The LLM answer containing the list of types.
        imports (set[str]): The set of import statements.

    Raises:
        ValueError: If the LLM answer does not conform to the expected list syntax.

    Returns:
        list[str] | Exception: A list of validated types or an exception.
    """
    cleaned = llm_answer.strip()
    cleaned = cleaned.replace("`", "").strip()
    cleaned = cleaned.replace('"', "").strip()
    cleaned = cleaned.replace("'", "").strip()

    if not (cleaned.startswith("[") and cleaned.endswith("]")):
        raise ValueError(f"Expected list syntax '[...]', got: {cleaned}")

    # Drop outer brackets
    inner = cleaned[1:-1].strip()

    items = [item.strip() for item in inner.split(",")]

    sanitized = []
    for item in items:
        t = validate_type(item, imports)
        sanitized.append(t)
    return sanitized


def validate_type(llm_answer: str, imports: set[str]) -> str | Exception:
    """Validates a single type provided by the LLM answer.

    Args:
        llm_answer (str): The LLM answer containing the type.
        imports (set[str]): The set of import statements.

    Raises:
        ValueError: If the LLM answer is not a string.
        ValueError: If the type entry is invalid.

    Returns:
        str | Exception: The validated and sanitized type or an exception.
    """
    if not isinstance(llm_answer, str):
        raise ValueError(f"Expected a type, got {type(llm_answer).__name__}")

    sanitized = ""
    try:
        sanitized = sanitize_and_validate(llm_answer, imports)
    except Exception as e:
        raise ValueError(f"Invalid type entry '{llm_answer}': {e}") from e

    return sanitized


def sanitize_and_validate(t: str, imports: set[str]) -> str:
    """Sanitizes and validates a type name.

    Args:
        t (str): The type name to sanitize and validate.
        imports (set[str]): The set of import statements.

    Raises:
        ValueError: If the type name is unknown or unsupported.

    Returns:
        str: The sanitized and validated type name.
    """
    sanitized_t = sanitize(t)

    if not is_valid_type(sanitized_t, imports):
        raise ValueError(f"Unknown or unsupported type name: '{sanitized_t}'")

    return sanitized_t


def sanitize(t: str) -> str | ValueError:
    """Sanitizes a type name by removing extraneous characters and validating its format.

    Args:
        t (str): The type name to sanitize.

    Raises:
        TypeError: If the type name is not a string.
        ValueError: If the type name contains invalid characters.

    Returns:
        str|ValueError: The sanitized type name or a ValueError if invalid.
    """
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
    match = re.match(r"^(\w+)", t.strip().lower())  # get root type

    if match:
        t = match.group(1)

    if any(ch in t for ch in ["(", ")", "[[", "{", "}"]):
        raise ValueError(f"Invalid characters in type name: '{t}'")
    return t


def validate_tags(llm_answer: str) -> list[str] | Exception:
    """Validates a list of tags provided by the LLM answer.

    Args:
        llm_answer (str): The LLM answer containing the list of tags.

    Raises:
        ValueError: If the LLM answer is not a valid Python literal.
        ValueError: If the LLM answer is not a list.
        ValueError: If any tag in the list is not a string.

    Returns:
        list[str] | Exception: A list of validated tags or an exception.
    """
    try:
        value = ast.literal_eval(llm_answer.strip())
    except Exception as e:
        raise ValueError(f"Invalid Python literal for tags list: {e}") from e
    if not isinstance(value, list):
        raise ValueError("Expected a list of tags string.")
    if not all(isinstance(tag, str) for tag in value):
        raise ValueError("All tags must be strings.")

    return value


def valid_category(answer_LLM: str, function_types: list[str]) -> bool:
    """Validates a single category provided by the LLM answer.

    Args:
        answer_LLM (str): The LLM answer containing the category.
        function_types (list[str]): The list of valid function types.

    Raises:
        ValueError: If the category is not in the list of valid function types.

    Returns:
        bool: True if the category is valid, otherwise raises a ValueError.
    """
    ans = answer_LLM.strip()
    ans = ans.replace('"', "").replace("'", "")
    if not in_list(ans, function_types):
        raise ValueError(f"Invalid category: {ans}")
    else:
        return True


def infer_python_type_from_ast(node: ast) -> str:
    """Infers the Python type from an AST node.

    Args:
        node (ast): The AST node to infer the type from.

    Returns:
        str: The inferred Python type as a string.
    """
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


def is_valid_type(expr: str, imports: set[str]) -> bool:
    """Checks if a given type expression is valid based on known base types and imported types.

    Args:
        expr (str): The type expression to validate.
        imports (set[str]): A set of imported type names to consider valid.

    Returns:
        bool: True if the type expression is valid, False otherwise.
    """
    return expr in (VALID_BASE_TYPES | imports)


def in_range(value: int, min_val: int, max_val: int) -> bool:
    """Checks if a value is within a specified range.

    Args:
        value (int): The value to check.
        min_val (int): The minimum acceptable value.
        max_val (int): The maximum acceptable value.

    Returns:
        bool: True if the value is within the specified range, False otherwise.
    """
    return min_val <= value <= max_val


def index_of(dicts: list[dict], key: str, value: any) -> int:
    """Finds the index of the first dictionary in a list where the specified key has the given value.

    Args:
        dicts (list[dict]): The list of dictionaries to search.
        key (str): The key to look for in each dictionary.
        value (any): The value to match against the specified key.

    Returns:
        int: The index of the first dictionary where the key matches the value, or -1 if not found.
    """
    for i, d in enumerate(dicts):
        if d.get(key) == value:
            return i
    return -1  # or None


def in_list(value: str, list_str: list[str]) -> bool:
    """Checks if a string value is present in a list of strings, case-insensitively.

    Args:
        value (str): The string value to check.
        list_str (list[str]): The list of strings to search within.

    Returns:
        bool: True if the string value is present in the list, False otherwise.
    """
    low_val = value.lower()
    for items in list_str:
        if items.lower() == low_val:
            return True
    return False


def write_functions_to_json(functions: list[dict], output: str) -> str:
    """Writes a list of function dictionaries to a JSON file.

    Args:
        functions (list[dict]): The list of function dictionaries to write.
        output (str): The output file path or base name for the JSON file.

    Returns:
        str: The path to the written JSON file, or an empty string if writing failed.
    """
    try:
        base_name = os.path.basename(output)
        base_name_no_ext = os.path.splitext(base_name)[0]
        base_output_name = f"results/{base_name_no_ext}_func_concepts"
        output_file = next_available_filename(base_output_name, ext="json")
        func_with_file = [{"file": base_name}] + functions
        with open(output_file, "w", encoding="utf-8") as out:
            json.dump(func_with_file, out, indent=4, ensure_ascii=False)

        print(f"[OK] JSON written: {output_file}")
        return output_file

    except Exception as e:
        print(f"[ERROR] Failed to write JSON: {e}")
        return ""
