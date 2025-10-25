import os
from openai import OpenAI
from dotenv import load_dotenv
from util import find_functions, get_json, list_files, read_file, write_file
from local import (
    FUNCTION_INSTANCE,
    HIERARCHY_NOTE,
    THINKING_STEPS,
    PERSONA,
    DEPTHS,
    RULES,
)
import json

models = [
    "moonshotai/Kimi-K2-Instruct-0905",
    "deepseek-ai/DeepSeek-V3.1",
    "meta-llama/Llama-3.1-8B-Instruct",
]


def analyze_file_with_llm(
    filepath: str,
    schema_dict: dict,
    d_i: int = 0,
    function_types_guide: str = "",
    model: str = "meta-llama/Llama-3.1-8B-Instruct",
    show_reasoning: bool = False,
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
        schema_dict,
        model,
        depth_index,
        function_types_guide,
        content,
        functions,
        show_reasoning,
    )
    # projection_res = get_projection()
    return concept_res.choices[0].message.content


def get_concept(
    schema_dict,
    model,
    depth_index,
    function_types_guide,
    content,
    functions,
    show_reasoning,
):
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": PERSONA},
            {"role": "system", "content": RULES},
            {"role": "system", "content": FUNCTION_INSTANCE},
            {"role": "system", "content": THINKING_STEPS},
            {"role": "system", "content": HIERARCHY_NOTE},
            {"role": "system", "content": f"FUNCTION_TYPES_GUIDE_START\n{function_types_guide}\nFUNCTION_TYPES_GUIDE_END\n"
            "Always pick the closest match from this list; do not generate new labels."},
            {"role": "user", "content": DEPTHS[depth_index]},
            {
                "role": "system",
                "content": (
                    "Output rule: "
                    + (
                        "You must include a non-null 'reasoning' field for every function instance. "
                        "Each reasoning must briefly explain why that function_type was chosen."
                        if show_reasoning
                        else "Set the 'reasoning' field of every function instance to null."
                    )
                ),
            },
            {
                "role": "user",
                "content": f"Classify every function {functions} listed in this file:\n\n{content}",
            },
        ],
    )


if __name__ == "__main__":
    load_dotenv()

    model_in_use = models[2]
    show_reasoning = True
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
        filepath = f"code/{file}"
        _ = read_file(filepath)
        print(f"--- {file} ---")
        _, functions = find_functions(filepath)
        print(f"Functions found in {filepath}: {functions}")
        print()

    for i in range(3):
        filepath = f"code/{list_of_files[2]}"
        print(
            f"Analyzing file: {list_of_files[2]} with model {model_in_use} at depth {i}"
        )
        response = analyze_file_with_llm(
            filepath,
            concept_schema,
            d_i=i,
            model=model_in_use,
            function_types_guide=function_types_guide,
            show_reasoning=show_reasoning,
        )
        analysis_output_path = f"results/analysis_{list_of_files[2]}_depth_{i}.txt"
        print(f"Writing results to {analysis_output_path}")
        write_file(analysis_output_path, response)
