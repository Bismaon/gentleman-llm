import os
from openai import OpenAI
from dotenv import load_dotenv
from util import find_functions, get_json, list_files, read_file, write_file
from local import (
    FUNCTION_INSTANCE,
    HIERARCHY_NOTE,
    FUNCTION_TYPES_GUIDE,
    THINKING_STEPS,
    PERSONA,
    DEPTHS,
    RULES,
)

models = [
    "moonshotai/Kimi-K2-Instruct-0905",
    "deepseek-ai/DeepSeek-V3.1",
    "meta-llama/Llama-3.1-8B-Instruct",
]


def analyze_file_with_llm(
    filepath: str,
    d_i: int = 0,
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
        content, functions = find_functions(filepath)
    except FileNotFoundError:
        return f"File not found: {filepath}"
    except Exception as e:
        return f"Error reading file {filepath}: {e}"
    pass
    concept_res = get_concept(
        model,
        depth_index,
        content,
        functions,
    )
    # projection_res = get_projection()
    return concept_res.choices[0].message.content


def get_concept(
    model,
    depth_index,
    content,
    functions,
):
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": PERSONA},
            {"role": "system", "content": RULES},
            {"role": "system", "content": FUNCTION_INSTANCE},
            # {"role": "system", "content": THINKING_STEPS},
            {"role": "system", "content": HIERARCHY_NOTE},
            {"role": "system", "content": FUNCTION_TYPES_GUIDE},
            {"role": "user", "content": DEPTHS[depth_index]},
            {
                "role": "user",
                "content": f"Classify every function {functions} listed in this file:\n\n{content}",
            },
        ],
    )


def pretty_LLM_flow(model_in_use, list_of_files, i, analysis_output_path):
    filepath = f"code/{list_of_files[2]}"
    print(
            f"Analyzing file: {list_of_files[2]} with model {model_in_use} at depth {i}"
        )
    response = analyze_file_with_llm(
            filepath,
            d_i=i,
            model=model_in_use,
        )
    print(f"Writing results to {analysis_output_path}")
    write_file(analysis_output_path, response)



if __name__ == "__main__":
    load_dotenv()

    model_in_use = models[2]
    show_reasoning = True
    d_i = 0  # depth index
    # concept_schema = get_json("formats/concept_format.json")
    # projection_schema = get_json("formats/projection_format.json")

    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.getenv("HF_TOKEN"),
    )

    list_of_files = list_files("code")
    for file in list_of_files:
        filepath = f"code/{file}"
        _ = read_file(filepath)
        print(f"--- {file} ---")
        _, functions = find_functions(filepath)
        print(f"Functions found in {filepath}: {functions}")
        print()

    for num_tries in range(10):
        analysis_output_path = f"results/analysis_{list_of_files[2]}_depth_{d_i}_try_{num_tries}.txt"
        pretty_LLM_flow(model_in_use, list_of_files, d_i, analysis_output_path)
