import ast
import json
import os

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

def find_functions(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    functions = extract_defined_functions(filepath)
    return content,functions

def extract_defined_functions(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # doc = ast.get_docstring(node)
            functions.append({
                "name": node.name,
                # "doc": doc or "",
            })
    return functions