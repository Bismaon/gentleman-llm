from time import sleep
import os
from openai import OpenAI
from dotenv import load_dotenv
from util import extract_information, get_json, in_list, in_range, list_files, read_file, time_step, valid_category, validate_tags, validate_type, validate_types, write_file, write_function_definitions
from local import (
    FUNCTION_INSTANCE,
    FUNCTION_TYPES_LIST,
    HIERARCHY_NOTE,
    FUNCTION_TYPES_GUIDE,
    THINKING_STEPS,
    PERSONA,
    DEPTHS,
    RULES,
    MAX_RETRY,
    MAX_EX_RETRY
)

models = [
    "moonshotai/Kimi-K2-Instruct-0905",
    "deepseek-ai/DeepSeek-V3.1",
    "meta-llama/Llama-3.1-8B-Instruct",
]

def ask(model:str, user_query:str, system:list[str], tries:int=0, error:str|None=None, ex_tries:int=0)->str|Exception:
    messages = []
    for system_query in system:
        messages.append({"role": "system", "content": system_query})
    if error:
        messages.append({
            "role": "system",
            "content": f"The previous attempt failed with this error:\n{error}\n"
        })
    messages.append({"role": "user", "content": user_query})
    
    try:
        response = client.chat.completions.create(model=model, messages=messages)
    except Exception as e:
        err = str(e).lower()
        if "exceeded" in err:
            ex_tries+=1
            wait = 2 ** (ex_tries+3)
            print(f"Exceeded monthly included credits (false), retrying in {wait} seconds...")
            sleep(wait)
            if ex_tries >= MAX_EX_RETRY:
                raise RuntimeError("Exceeded maximum retries for exceeded credits.") from e
            return ask(model, user_query, system, tries, error, ex_tries)
        elif "timeout" in err:
            raise TimeoutError("Request timed out.") from e
        else:
            raise e
    
        
    answer = response.choices[0].message.content
    if answer is None:
        raise SystemError("No answer from the model.")
    return answer
    

def define_param_types(function_info:dict, model:str, imports):
    system = [
        "You are a code analysis assistant.",
        "You will be given a Python function source and a list of its parameters.",
        "If a parameter's type is unclear or is from a dependency, use `any` as its type.",
        "Respond ONLY with a Python list of type names."
    ]

    param_names = function_info['parameters'].keys()
    code = function_info['source']
    user_query = f"""
    Function Source:
    {code}

    Parameters:
    {param_names}
    """
    param_len = len(param_names)
    parsed_types = []
    tries = 0
    last_error = None
    while len(parsed_types) != param_len:
        try:
            answer = ask(model, user_query, system, tries, error=last_error)
            parsed_types = validate_types(answer, imports)
            print(f"Parsed Types for {param_names} after {tries} tries:\n{parsed_types}\n")
        except Exception as e:
            print(f"Attempt {tries} failed: {e}")
            last_error = str(e)
            tries += 1
            if tries >= MAX_RETRY:
                raise RuntimeError(f"Failed to define parameter types after {tries} tries: {e}")
            continue
    return parsed_types

def define_tags(function_info:dict, content:str, model:str, max_tags:int=5)->list[str]|Exception:
    system = [
        "You are a code analysis assistant.",
        "You will be given a Python file, a function source and its description.",
        f"Extract up to {max_tags} relevant tags that describe ONLY the function source's purpose, behavior, and role.",
        "Respond ONLY with a Python list of tags string."
    ]

    name = function_info['name']
    code = function_info['source']
    desc = function_info['description']
    user_query = f"""
    File:
    {content}
    
    Function Source:
    {code}

    Description:
    {desc}
    """
    parsed_tags = []
    tries = 0
    last_error = None
    while len(parsed_tags) == 0:
        try:
            answer = ask(model, user_query, system, tries, error=last_error)
            parsed_tags = validate_tags(answer)
            print(f"Parsed Tags for {name} after {tries} tries:\n{parsed_tags}\n")

        except Exception as e:
            print(f"Attempt {tries} failed: {e}")
            last_error = str(e)
            tries += 1
            if tries >= MAX_RETRY:
                raise RuntimeError(f"Failed to define tags after {tries} tries: {e}")
            continue
        
    return parsed_tags

def define_description(function_info:dict, content:str, model:str, min_len:int=100, max_len:int=250)->list[str]|Exception:
    system = [
        "You are a code analysis assistant.",
        "You will be given a Python file, a function source, and its parameters.",
        f"Generate a concise description ONLY of the function source, on its role, purpose, and behavior in the file, between {min_len} and {max_len} characters.",
        "Respond ONLY with the description string."
    ]

    name = function_info['name']
    params = function_info['parameters']
    code = function_info['source']
    user_query = f"""
    File:
    {content}
    
    Function:
    {code}

    Parameters and Types:
    {params}
    """
    parsed_desc = ""
    tries = 0
    last_error = None
    while not in_range(len(parsed_desc), min_len, max_len):
        try:
            answer = ask(model, user_query, system, tries, error=last_error)

            if not in_range(len(answer), min_len, max_len):
                last_error = f"Description length {len(answer)} out of bounds."
                tries += 1
                continue
            
            parsed_desc = answer
            print(f"Parsed Description for {name} after {tries} tries:\n{parsed_desc}\n")

        except Exception as e:
            print(f"Attempt {tries} failed: {e}")
            last_error = str(e)
            tries += 1
            if tries >= MAX_RETRY:
                raise RuntimeError(f"Failed to define description after {tries} tries: {e}")
    return parsed_desc

def define_return_type(function_info:dict, model:str, imports):
    system = [
        "You are a code analysis assistant.",
        "You will be given a Python function source, a list of its parameters and their types, and its return value.",
        "If a return's type is unclear or is from a dependency, use `any` as its type.",
        "Respond ONLY with a the return type of the function."
    ]

    params = function_info['parameters'].keys()
    code = function_info['source']
    if not function_info["return"]:
        return_value = "None"
    else:
        return_value, return_type = next(iter(function_info["return"].items()))
        if (return_type!=""):
            return return_type

    user_query = f"""
    Function Source:
    {code}

    Parameters and their types:
    {params}

    Return value:
    {return_value}
    """
    return_type = ""
    tries = 0
    last_error = None
    while return_type=="":
        try:
            answer = ask(model, user_query, system, tries, error=last_error)
            return_type = validate_type(answer, imports)
            print(f"Parsed Type for {return_value} atfer {tries} tries:\n{return_type}\n")
        except Exception as e:
            print(f"Attempt {tries} failed: {e}")
            last_error = str(e)
            tries += 1
            if tries >= MAX_RETRY:
                raise RuntimeError(f"Failed to define return type after {tries} tries: {e}")
            continue
    return return_type


def define_category(function_info:dict, content:str, model:str)->str|Exception:
    system = [
        "You are a code analysis assistant.",
        "You will be given a Python function source, its description, tags, parameters, and return value.",
        "Using FUNCTION_TYPES_GUIDE, determine which function category best describes the function.",
        "Respond ONLY with a single string: the chosen function type.",
        "Valid categories are the ones listed in FUNCTION_TYPES_GUIDE."
    ]


    name = function_info['name']
    params = function_info['parameters']
    code = function_info['source']
    description = function_info['description']
    tags = function_info['tags']
    return_ = function_info['return']
    user_query = f"""
    FUNCTION_TYPES_GUIDE:
    {FUNCTION_TYPES_GUIDE}

    Function Source:
    {code}

    Description:
    {description}

    Tags:
    {tags}

    Parameters and Types:
    {params}

    Return Value and type:
    {return_}
    """

    category = ""
    tries = 0
    last_error = None
    while not in_list(category, FUNCTION_TYPES_LIST):
        try:
            answer = ask(model, user_query, system, tries, error=last_error)
            print(f"Category answer: {answer}")

            if not valid_category(answer, FUNCTION_TYPES_LIST):
                last_error = f"Category is not a valid function category: {category}."
                tries += 1
                continue
            
            category = answer
            print(f"Parsed category for {name} after {tries} tries:\n{category}\n")

        except Exception as e:
            print(f"Attempt {tries} failed: {e}")
            last_error = str(e)
            tries += 1
            if tries >= MAX_RETRY:
                raise RuntimeError(f"Failed to define category after {tries} tries: {e}")
    return category

if __name__ == "__main__":
    load_dotenv()

    model_in_use = models[2]
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.getenv("HF_TOKEN"),
    )
    base = "code"
    list_of_files = list_files(base)

    for file in list_of_files:
        filepath = f"{base}/{file}"
        print(f"--- {file} ---")
        functions, imports = time_step(
            "Extract information",
            extract_information,
            filepath
        )
        content = read_file(filepath)
        
        for func in functions:
            # Parameter Types
            answer_types = time_step(
                f"{func['name']} - Param Types",
                define_param_types,
                func,
                model_in_use
            )
            func["parameters"] = dict(zip(func['parameters'].keys(), answer_types))

            # Tags
            func["tags"] = time_step(
                f"{func['name']} - Tags",
                define_tags,
                func,
                content,
                model_in_use
            )

            # Description
            func["description"] = time_step(
                f"{func['name']} - Description",
                define_description,
                func,
                content,
                model_in_use
            )

            # Return Type
            answer_return = time_step(
                f"{func['name']} - Return Type",
                define_return_type,
                func,
                model_in_use
            )
            func["return"] =dict(zip(func['return'].keys(), [answer_return]))

            # Category
            func["category"] = time_step(
                f"{func['name']} - Category",
                define_category,
                func,
                content,
                model_in_use
            )

        # Write output timing
        time_step(
            f"{file} - Writing Function Definitions",
            write_function_definitions,
            filepath,
            functions
        )
