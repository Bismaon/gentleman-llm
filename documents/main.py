from time import sleep
import os
from openai import OpenAI
from dotenv import load_dotenv
from util import extract_functions, get_json, list_files, read_file, validate_types, write_file, write_function_definitions
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

def ask(model:str, user_query:str, system:list[str], tries:int=0)->str:
    messages = []
    for system_query in system:
        messages.append({"role": "system", "content": system_query})
    messages.append({"role": "user", "content": user_query})
    
    try:
        response = client.chat.completions.create(model=model, messages=messages)
    except Exception as e:
        err = str(e).lower()
        if "exceeded" in err:
            wait = 2 ** tries
            print(f"Exceeded monthly included credits (false), retrying in {wait} seconds...")
            sleep(wait)
            if tries >=5:
                return e
            return ask(model, user_query, system, tries+1)
        elif "timeout" in err:
            return TimeoutError("Request timed out.")
        else:
            return e
        
    answer = response.choices[0].message.content
    if answer is None:
        return SystemError("No answer from the model.")
    return answer
    

def define_functions(function_info:dict, model:str):
    system = [
    "You are a code analysis assistant.",
    "You will be given a Python function definition and a list of its parameters.",
    "If a parameter's type is a database object like `MongoDB`, write its type as `DB`.",
    "If a parameter's type is unclear or is dependency, use `any` as its type.",
    "Respond ONLY with a Python list of type names."
    ]

    name = function_info['name']
    param_names = function_info['parameters']
    code = function_info['source']
    user_query = f"""
    Function:
    {code}

    Parameters:
    {param_names}

    Return exactly one inferred type per parameter in a Python list, nothing else.
    """
    param_len = len(param_names)
    parsed_types = []
    while len(parsed_types) != param_len:
        
        try:
            answer = ask(model, user_query, system)

            parsed = validate_types(answer)
            if isinstance(parsed, Exception):
                print(f"Error parsing LLM output: {parsed}\nRetrying...\n")
                continue

            parsed_types = parsed
            print(f"Parsed Types: {parsed_types} for {param_names}\n")

        except Exception as e:
            return e
        if len(parsed_types) != param_len:
            print("Retrying type definition...\n")
    
    
    return parsed_types



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
    base = "code"
    list_of_files = list_files(base)
    for file in list_of_files:
        filepath = f"{base}/{file}"
        _ = read_file(filepath)
        print(f"--- {file} ---")
        functions = extract_functions(filepath)
        for func in functions:
            answer_types = define_functions(func, model_in_use)
            if isinstance(answer_types, Exception):
                print(f"Error defining types for function {func['name']}: {answer_types}\n")
            else:
                func['types'] = answer_types
            print(f"Function: {func['name']}\nDefined Types:\n{func["types"]}\n")
        write_function_definitions(filepath, functions)
    
    # for num_tries in range(3):
    #     analysis_output_path = f"results/analysis_{list_of_files[2]}_depth_{d_i}_try_{num_tries}.txt"
    #     pretty_LLM_flow(model_in_use, list_of_files, d_i, analysis_output_path)
