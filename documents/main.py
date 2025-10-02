import os
from openai import OpenAI
from dotenv import load_dotenv
from local import FUNCTION_TYPES_GUIDE

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
    
def analyze_file_with_llm(directory: str, filename: str, model: str = "moonshotai/Kimi-K2-Instruct-0905") -> str:
    """
    Reads a file and sends its content to the LLM for analysis.
    
    Parameters
    ----------
        directory : str
            Path to the directory containing the file.
        filename : str
            Name of the file to analyze.
        model : str
            Model to use (default: Kimi K2 Instruct).
    
    Returns
    -------
    str 
        The LLM response text.
    """
    filepath = os.path.join(directory, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return f"File not found: {filepath}"
    except Exception as e:
        return f"Error reading file {filepath}: {e}"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a Python code analyzer."},
            {"role": "user", "content": FUNCTION_TYPES_GUIDE},
            {"role": "user", "content": f"Classify every function in this file:\n\n{content}"}
        ],
    )

    return response.choices[0].message.content
load_dotenv()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_TOKEN"),
)

# print(completion.choices[0].message)
list_of_files = list_files("code")
for file in list_of_files:
    content = read_file("code", file)
    print(f"--- {file} ---")
    print()

response = analyze_file_with_llm("code", list_of_files[2])
write_file("results", f"analysis_{list_of_files[2]}", response)
