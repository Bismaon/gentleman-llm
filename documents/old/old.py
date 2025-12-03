# import json
# # import logging
# import os
# # import time
# from util import VALID_BASE_TYPES, next_available_filename


# logging.basicConfig(
#     filename="timing.log",
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
# )

# logger = logging.getLogger(__name__)

# def write_valid_types(file:str,plus:set[str]|None=None, output_path="results/valid_types"):
#     try:
#         out = next_available_filename(f"{output_path}_{file}")
#         with open(out, "w", encoding="utf-8") as f:
#             for t in list(VALID_BASE_TYPES):
#                 f.write(f"{t}\n")
#             for t in list(plus):
#                 f.write(f"{t}\n")
#         print(f"[OK] Valid types written to {out}")
#     except Exception as e:
#         print(f"[ERROR] Cannot write valid types: {e}")


    
# def get_json(filename: str) -> dict:
#     """
#     Load and return the JSON from the `filename` file.

#     Parameters
#     ----------
#         filename : str
#             JSON filename.

#     Returns
#     -------
#         dict
#             The JSON.
#     """
#     try:
#         with open(filename, "r", encoding="utf-8") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         print(f"JSON file not found: {filename}")
#         return {}
#     except json.JSONDecodeError:
#         print("Error decoding JSON from file.")
#         return {}
#     except Exception as e:
#         print(f"Error loading JSON: {e}")
#         return {}

# def write_function_definitions(filepath: str, functions: list[dict]) -> None:
#     base_name = os.path.splitext(os.path.basename(filepath))[0]
#     base_output_name = f"results/{base_name}_func_def"
#     output_file = next_available_filename(base_output_name)

#     with open(output_file, "w", encoding="utf-8") as f:
#         for i, func in enumerate(functions, start=1):
#             f.write(
#                 f"--- Function {i}: {func['name']} - {func["start_line"]}:{func["end_line"]}---"
#             )
#             f.write(f"\n# Source:\n{func["source"]}")
#             params = "("
#             for param, p_type in func["parameters"]:
#                 params += f"{param}: {p_type},"
#             params += ")"
#             f.write(f"\n\n# Parameters:\n{params}")
#             return_value, return_type = func["return"]

#             f.write(f"\n# Returns:\n{return_value}:{return_type}")
#             f.write(f"\n# Category:\n{func['category']}")
#             f.write(f"\n# Description:\n{func['description']}")
#             f.write(f"\n# Tags:\n{', '.join(func['tags'])}")
#             f.write(f"\n# Calls:\n{', '.join(func['calls'])}")
#             f.write(f"\n# Called by:\n{', '.join(func['called_by'])}")
#             f.write("\n\n")

#     print(f"Wrote {len(functions)} function definitions to {output_file}")

# def time_step(label: str, func, *args, **kwargs):
#     start = time.perf_counter()
#     try:
#         result = func(*args, **kwargs)
#         end = time.perf_counter()
#         logger.info(f"[TIME] {label}: {end - start:.3f} seconds")
#         return result
#     except Exception as e:
#         end = time.perf_counter()
#         logger.error(
#             f"[TIME ERROR] {label} failed after {end - start:.3f} seconds "
#             f"with exception: {e}"
#         )
#         raise

