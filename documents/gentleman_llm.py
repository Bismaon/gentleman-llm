import os
from time import sleep
from openai import OpenAI
from util import (
    VALID_BASE_TYPES,
    extract_information,
    validate_types,
    validate_tags,
    validate_type,
    in_range,
    valid_category,
)
from local import (
    FUNCTION_TYPES_LIST,
    FUNCTION_TYPES_GUIDE,
)


class GentlemanLLM:
    def __init__(self, hf_token: str, model: str):
        self.model = model
        self.client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=hf_token,
        )
        self.ex_retries = 0
        self.max_retry = 10
        self.max_ex_retry = 5

    def ask(
        self, user_query: str, system: list[str], error: str | None = None
    ) -> str | RuntimeError:
        """Queries the llm with the user query, and system query. Optionally error if the last the last query with the LLM was unsuccessful.

        Args:
            user_query (str): a list of user queries
            system (list[str]): a list of system queries
            error (str | None, optional): The last error if the previous query was unsuccesful. Defaults to None.

        Raises:
            RuntimeError: The LLM did not return anything.

        Returns:
            (str|RuntimeError): The answer of the model.
        """
        messages = [{"role": "system", "content": s_query} for s_query in system]
        if error:
            messages.append(
                {"role": "system", "content": f"Previous attempt failed:\n{error}"}
            )
        messages.append({"role": "user", "content": user_query})

        resp = self.client.chat.completions.create(model=self.model, messages=messages)
        answer = resp.choices[0].message.content
        if not answer:
            raise RuntimeError("Model returned no output.")
        return answer

    # Define functions
    def define_param_types(
        self, function_info: dict, imports: set[str]
    ) -> list[str] | Exception:
        """Defines the types of each parameters of a function.

        Args:
            function_info (dict): The dictionnary containing the function's information.
            imports (set[str]): The set containing all of the imports of the function's file, used to match types with LLM answer.

        Returns:
            (list[str] | Exception): A list of the types of each parameters. Or an exception if the LLM's answer is not valid.
        """
        system = [
            "You are a code analysis assistant.",
            "You will be given a Python function source and a list of its parameters.",
            "Define each parameter's type.",
            f"Parameters types accepted: {VALID_BASE_TYPES}",
            "Respond ONLY with a Python list of types.",
        ]

        p_names = [name for name, _ in function_info["parameters"]]
        code = function_info["source"]
        query = f"Function:\n{code}\n\nParameters:\n{p_names}"

        p_len = len(p_names)
        last_error = None
        tries = 0
        while True:
            try:
                answer = self.ask(query, system, error=last_error)
                types = validate_types(answer, imports)

                len_ans = len(types)
                if len_ans == p_len:
                    return types
                elif len_ans > p_len:
                    last_error = (
                        f"Too many types given.\nGiven: {len_ans}, Expected: {p_len}."
                    )
                else:
                    last_error = (
                        f"Not enough types given.\nGiven: {len_ans}, Expected: {p_len}."
                    )
                tries += 1

            except Exception as e:
                name = "parameter types"
                last_error, tries = self.exception_handler(name, tries, e)

    def define_tags(
        self, function_info: dict, content: str, max_tags: int = 5
    ) -> list[str] | Exception:
        """Defines `max_tags` tags for the function.

        Args:
            function_info (dict): The dictionnary containing the function's information.
            content (str): The whole content of the function's file.
            max_tags (int, optional): The number of tags to define for the function. Defaults to 5.

        Returns:
            (list[str] | Exception): A list of the tags. Or an exception if the LLM's answer isn't valid.
        """
        system = [
            "You are a code analysis assistant.",
            "You will be given a Python file, a function source and its description.",
            f"Extract up to {max_tags} relevant tags that describe ONLY the function source's purpose, behavior, and role.",
            "Respond ONLY with a Python list of tags string.",
        ]
        query = f"File content:\n{content}\nFunction source:\n{function_info['source']}\nDescription of function:\n{function_info['description']}"
        last_error = None
        tries = 0
        while True:
            try:
                answer = self.ask(query, system, last_error)
                tags = validate_tags(answer)
                tries += 1
                return tags
            except Exception as e:
                name = "tags"
                last_error, tries = self.exception_handler(name, tries, e)

    def define_description(
        self, function_info: dict, content: str, min_len=50, max_len=200
    ) -> str | Exception:
        """Define the description of the function.

        Args:
            function_info (dict): The dictionnary containing the function's information.
            content (str): The whole content of the function's file.
            min_len (int, optional): The minimum length of the description. Defaults to 50.
            max_len (int, optional): The maximum length of the description. Defaults to 200.

        Returns:
            (str | Exception): The description of the function. Or an exception if the LLM's answer isn't valid.
        """
        system = [
            "You are a code analysis assistant.",
            "You will be given a Python file, a function source, and its parameters.",
            f"Generate a concise description ONLY of the function source, on its role, purpose, and behavior in the file, between {min_len} and {max_len} characters.",
            "Respond ONLY with the description string.",
        ]
        source = function_info["source"]
        parameters = function_info["parameters"]
        query = f"File content:\n{content}\nFunction source:\n{source}\nParameters:\n{parameters}"
        last_error = None
        tries = 0

        while True:
            try:
                answer = self.ask(query, system, last_error)

                len_ans = len(answer)
                if in_range(len_ans, min_len, max_len):
                    return answer
                elif len_ans < min_len:
                    tries += 1
                    last_error = f"Description is too short.\nGiven:{len_ans}, Expected at least: {min_len}."
                else:
                    tries += 1
                    last_error = f"Description is too long.\nGiven:{len_ans}, Expected at most: {max_len}."

            except Exception as e:
                name = "description"
                last_error, tries = self.exception_handler(name, tries, e)

    def define_return_type(
        self, function_info: dict, imports: set[str]
    ) -> str | Exception:
        """Define the return type of the function.

        Args:
            function_info (dict): The dictionnary containing the function's information.
            imports (set[str]): The set containing all of the imports of the function's file, used to match types with LLM answer.

        Returns:
            (str | Exception): The return type of the function. Or an exception if the LLm's answer isn't valid.
        """
        r_value, r_type = function_info["return"]
        if r_value == "" and r_type == "":
            return "None"
        if r_type != "any":  # type is already defined
            return r_type

        system = [
            "You are a code analysis assistant.",
            "You will be given a Python function source, a list of its parameters and their types, and its return value.",
            "If a return's type is unclear or is from a dependency, use `any` as its type.",
            "Respond ONLY with a the return type of the function.",
        ]
        source = function_info["source"]
        parameters = function_info["parameters"]
        query = (
            f"Function source:\n{source}\nParameters:\n{parameters}\nReturn:\n{r_value}"
        )
        last_error = None
        tries = 0

        while True:
            try:
                answer = self.ask(query, system, last_error)
                return_type = validate_type(answer, imports)
                tries += 1
                return return_type
            except Exception as e:
                name = "return type"
                last_error, tries = self.exception_handler(name, tries, e)

    def define_category(self, function_info: dict) -> str | Exception:
        """Define the category of the function.

        Args:
            function_info (dict): The dictionnary containing the function's information.

        Returns:
            str | Exception: The category of the function. Or an exception if the LLm's answer isn't valid.
        """
        system = [
            "You are a code analysis assistant.",
            "You will be given a Python function source, its description, tags, parameters, and return value.",
            "Using FUNCTION_TYPES_GUIDE, determine which function category best describes the function.",
            "Respond ONLY with a single string: the chosen function type.",
            "Valid categories are the ones listed in FUNCTION_TYPES_GUIDE.",
        ]
        source = function_info["source"]
        parameters = function_info["parameters"]
        return_t = function_info["return"]
        tags = function_info["tags"]
        description = function_info["description"]
        query = f"""
        {FUNCTION_TYPES_GUIDE}

        Function source:
        {source}
        
        Description:
        {description}

        Parameters:
        {parameters}

        Return:
        {return_t}

        Tags:
        {tags}        
        """

        last_error = None
        tries = 0
        while True:
            try:
                answer = self.ask(query, system, last_error).strip()
                tries += 1

                if valid_category(answer, FUNCTION_TYPES_LIST):
                    return answer

                last_error = f"Category is not a valid function category: {answer}."

            except Exception as e:
                name = "category"
                last_error, tries = self.exception_handler(name, tries, e)

    def analyze_file(self, filepath: str) -> list[dict] | RuntimeError:
        """Defines the all of the function's in the file.

        Args:
            filepath (str): The file containing the code.

        Raises:
            RuntimeError: The LLM failed to define the function's of the file.

        Returns:
            (list[dict] | Exception): The function defined in a list. Or an Exception if the LLM failed to define the functions.
        """
        functions, imports, content = extract_information(filepath)

        for f in functions:
            try:
                f["parameters"] = [
                    (name, t)
                    for (name, _), t in zip(
                        f["parameters"], self.define_param_types(f, imports)
                    )
                ]

                f["tags"] = self.define_tags(f, content)
                f["description"] = self.define_description(f, content)
                f["return"] = (f["return"][0], self.define_return_type(f, imports))
                f["category"] = self.define_category(f)
            except Exception as e:
                raise RuntimeError(f"Failed to define function {f['name']}: {e}")

        base_name = os.path.basename(filepath)
        json_output = [{"file": base_name}] + functions
        return json_output

    def exception_handler(
        self, name: str, tries: int, e: Exception
    ) -> tuple[str, int] | RuntimeError:
        """Handles the different exception returned by the LLM.

        Args:
            name (str): The name of the current step in the function definition.
            tries (int): The number of tries for the current step.
            e (Exception): The exception returned.

        Raises:
            RuntimeError: if the number of tries exceed `max_retry`, the LLM's failing to define the current step.

        Returns:
            ((str, int) | RuntimeError): The error to return to the LLM, and number of tries. Or an Exception if the number of retries have been exceeded.
        """
        err = str(e).lower()
        if "exceeded" in err:
            self.exceed_credits_handle(e)
        else:
            last_error = str(e)
            print(f"Attempt {tries} failed: {e}")
            tries += 1
            if tries >= self.max_retry:
                raise RuntimeError(f"Failed to define {name} after {tries} tries: {e}")
            return last_error, tries

    # Obsolete
    def exceed_credits_handle(self, e: Exception) -> int:
        """Handles the credit issue with Hugging Face.

        Args:
            e (Exception): Credit issue exception.

        Raises:
            RuntimeError: Number of retries have exceeded `max_ex_retry`.

        Returns:
            (int): The number of retries for the credit exception.
        """
        self.ex_tries += 1
        if self.ex_tries >= self.max_ex_retry:
            raise RuntimeError("Exceeded maximum retries for exceeded credits.") from e
        wait = 2**self.ex_tries
        print(
            f"Exceeded monthly included credits (false), retrying in {wait} seconds..."
        )
        sleep(wait)
        return self.ex_tries
