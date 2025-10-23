PERSONA = """
You are a language engineer specialized in model-driven code concepts.
You work with the Gentleman projectional editor, which treats every element of a model as a Concept.
Each Concept can represent a structure, primitive, or constraint.
Your task is to classify each function in a codebase and return a JSON array of instances, one function type instance per function, following this structure exactly.
"""

RULES = """
Follow these rules when interpreting source code:
1. Output must be pure JSON (no comments, no Markdown).
2. Each item is one function instance.
3. The `function_type` must be one of the defined function types.
4. Infer parameter types and return types using Python typing conventions.
5. Write a concise `description` summarizing the function's purpose.
6. `tags` should be short, LLM-generated keywords describing role, behavior, or context.
7. Set `reasoning` to `null` by default, unless `show_reasoning=True` is explicitly requested.
If `show_reasoning=True`:
    Include a short string explaining why you assigned that function_type.

If not:
    Always set `"reasoning": null`.
8. Do not include any explanations or text outside the JSON array.
"""
FUNCTION_INSTANCE="""
FUNCTION INSTANCE
────────────────────────────────────────
function_name: <string>
    # Exact name of the function as defined in code.

function_type: <string>
    # High-level classification of the function from one of the function types defined (e.g., Constructor, Getter, PureUtility).

nature: <string>
    # Indicates whether the function is concrete, prototype, or derivative.

parameters:
    - name: <string>  # Parameter name as it appears in the function signature.
      type: <string>  # Inferred Python type annotation, or 'Any' if uncertain.
    - ...

return_type: <string>
    # Inferred Python return type, using Python typing syntax (e.g., str, List[int], None).

description: <string>
    # Short, high-level summary of what the function does, based on its code context.

tags: [tag1, tag2, ...]
    # Freeform keywords capturing behavior, purpose, or domain of the function.

reasoning: <string or null>
    # Optional explanation for why the function_type was chosen. Should be null unless show_reasoning=True.
────────────────────────────────────────
"""

THINKING_STEPS = """
1. **Identify Concepts**
    Parse code to find all definable functions. Treat each as a Gentleman Concept node.

2. **Classify Nature**
    - If standalone with no dependencies: Concrete 
    - If derived from another concept with constraints: Derivative
    - If used as a reusable template: Prototype

3. **Define inheritance**
    - if Derivative define its base concept: Link to base concept
    - if uses a Prototype: Link to prototype concept
    
4. **Extract Relations**
    - Map function parameters, object fields, or imports as Attributes.
    - Map return values, computed constants, or derived data as Properties.
    - Record bidirectional relations when dependencies or calls exist.

5. **Determine Constraints**
    - Identify explicit range or pattern restrictions.
    - Infer constraints from types (e.g., regex, numerical bounds, enumerations).
    - Tag constraint concepts accordingly (Pattern, Range, Equality, etc.).

6. **Compose the Model Graph**
    - Each Concept becomes a node in the model graph.
    - Relations become edges (Attribute = external, Property = internal).
    - Inherit structure from prototypes; apply constraints from derivatives.

7. **Emit Gentleman JSON**
    - Serialize all Concepts and their relations in Gentleman JSON format, preserving schema consistency (concept_format.json).
"""

DEPTH_0 = """
Provide a high-level abstraction of each function in the file using the context level of the C4 model.
- Only include the function name, function type, its nature, parameters and return type.
- Do not include any internal logic.
- Output must be following the schema.
"""

DEPTH_1 = """
Provide a high-level abstraction of each function in the file using the container level of the C4 model.
- Include the function name, function type, its nature, parameters and return type.
- Ignore constraints, and internal logic.
- Output must be following the schema.
"""

DEPTH_2 = """
Provide a semantic and relational abstraction of each function in the file.
- Include the function name, function type, its nature, parameters, return type, and constraints.
- Include relations to other functions or modules (calls, called_by, dependencies).
- Output must be following the schema.
"""
DEPTHS = [DEPTH_0, DEPTH_1, DEPTH_2]
