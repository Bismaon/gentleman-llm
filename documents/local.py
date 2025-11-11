PERSONA = """
You are a language engineer specialized in model-driven code concepts.
Create the python doc for the store_data function.
"""
# instances of func across multiple files
RULES = """
Follow these rules when interpreting source code:
1. Each item is one function instance.
2. The `function_type` must be one of the defined function in `FUNCTION_TYPES_GUIDE`.
3. Infer parameter types and return types using Python types.
4. Write a concise `description` summarizing the function's purpose.
5. `tags` should be short keywords describing role, behavior, or context.
7. Each reasoning must explicitly state the main evidence for the chosen function_type using one of these patterns:
    - "classified as <type> because it [core behavior]"
    - "fits the <type> type since it [reason]"
"""

FUNCTION_INSTANCE="""
function_name: ff0

function_type: ff1
"""
# """
# parameters:
#     - name: <string>  # Parameter name as it appears in the function signature.
#       type: <string>  # Inferred Python type, or 'Any' if uncertain.

# return_type: <string>
#     # Inferred return Python type.

# description: <string>
#     # Short summary of what the function does, based on its code context.

# tags: [tag1, tag2, ...]
#     # Keywords capturing behavior, purpose, and/or domain of the function.

# reasoning: <string>
#     # Optional explanation for why the function_type was chosen.
# """

# other:
# nature: <string>
#     # Indicates whether the function is concrete, prototype, or derivative.
# inheritance:
#     - base_concept: <string or null> # If derivative, the name of the base concept; otherwise null.
#     - prototype_concept: <string or null> # If prototype, the name of the prototype concept; otherwise null.
    
# constraints:
#     - type: <string>  # Type of constraint (Pattern, Range, Equality, Match, or Values).
#       details: <string>  # Description of the constraint.

# relations:
#     - calls: [<function_name1>, <function_name2>, ...]  # Functions that this function calls.
#     - called_by: [<function_name1>, <function_name2>, ...]  # Functions that call this function.
#     - dependencies: [<concept_name1>, <concept_name2>, ...]  # Other concepts this function depends on.

THINKING_STEPS = """
1. **Identify Concepts**
    - Parse code to find all definable functions. Treat each as a Gentleman Concept node.

2. **Classify Nature**
    - If standalone with no dependencies: Concrete 
    - If derived from another concept with constraints: Derivative
    - If used as a reusable template: Prototype

3. **Define inheritance**
    - if Derivative define its base concept: Link to base concept
    - if uses a Prototype: Link to prototype concept

4. **Extract Parameters**
    - Map function parameters, object fields, or imports as Attributes.

5. **Extract Return values**
    - Map return values, computed constants, or derived data as Properties.

6. **Determine Constraints**
    - Identify explicit restrictions inside the function.
    - Infer constraints from types (e.g., regex, numerical bounds, enumerations).
    - Tag constraint concepts accordingly (Pattern, Range, Equality, Match, or Values).
"""

# HIERARCHY_NOTE = """
# Prompt precedence order (highest to lowest):
# 1. PERSONA — sets overall role and context.
# 2. FUNCTION_TYPES_GUIDE — the definitive classification for function_type labels.
# 3. RULES — governs format and schema.
# 4. DEPTH prompt — only controls *detail level*, not label meaning.
# 5. THINKING_STEPS — reasoning outline, not structural output.
# 6. FUNCTION_INSTANCE schema — output format only.
# !!Never invent function_type labels beyond `FUNCTION_TYPES_GUIDE`!!
# """

FUNCTION_TYPES_GUIDE="""
FUNCTION_TYPES_GUIDE_BEGIN
- Constructor:
    - MustHave:
        - Defines or initializes object state
        - Uses or mirrors class parameters (self, cls)
    - Optional:
        - Assigns instance attributes
        - Performs lightweight I/O strictly for initialization (loading configuration, reading defaults)
    - MustNotHave:
        - Standalone data processing or business logic
        - Returns computed results not tied to initialization
- Property:
    - MustHave:
        - Accesses or modifies object attributes directly
        - Short body (less than 3 statements)
    - Optional: 
        - Performs minimal validation on assigned values
        - Names match getter/setter/boolean patterns
    - MustNotHave: 
        - Creates new data structures or computations unrelated to attributes
        - Performs I/O or external calls
- PureUtility:
    - MustHave:
        - No dependency on object state (`self`, `cls`)
        - No I/O operations
        - Deterministic output based only on input parameters
    - Optional: 
        - Performs math, string, or data transformations
        - Used across modules as helper
    - MustNotHave: 
        - I/O operations
        - Global or external state access
        - File, network, or database access
        - Randomness or time dependence
        - Logging or printing
- TestFunction:
    - MustHave:
        - Contains assertions or test framework calls
        - Usually named with 'test_' prefix or '_test' suffix
    - Optional: 
        - No parameters or uses fixture injection
        - Raises exceptions upon failure
    - MustNotHave: 
        - Business logic or computation unrelated to testing
        - External I/O beyond mocks
- ExternalInteraction:
    - MustHave:
        - Performs communication with an external system, service, or persistent storage
        - Produces or consumes data exchanged outside the program's in-memory context
    - Optional: 
        - Accepts identifiers, paths, URLs, or connection handles as parameters
        - Reads or writes structured data (e.g., JSON, CSV, database rows, API payloads)
        - Implements protocols or query patterns (HTTP requests, SQL, ORM calls, caching operations)
        - Handles encoding, serialization, or deserialization
    - MustNotHave: 
        - Purely computational or formatting logic with no system interaction
        - Internal data transformation detached from external communication
FUNCTION_TYPES_GUIDE_END
"""

HIERARCHY_NOTE = """
Prompt precedence order (highest to lowest):
1. PERSONA — sets overall role and context.
2. FUNCTION_TYPES_GUIDE — the definitive classification for function_type labels.
3. FUNCTION_INSTANCE schema — output format only.
!!Never invent function_type labels beyond `FUNCTION_TYPES_GUIDE`!!
"""

DEPTH_0 = """
Classify each function only by its broad conceptual role.
- Output strictly follows `FUNCTION_INSTANCE` schema.
- Use `FUNCTION_TYPES_GUIDE` only.

- Provide a brief description of what the function does in the codebase.
- Provide relevant tags.
- Provide one-sentence reasoning.
- Extract parameters and return types.
"""

DEPTH_1 = DEPTH_0 + """
- Define internal constraints of the function.
"""

DEPTH_2 = DEPTH_1 + """
- Include relations (calls, called_by, dependencies).
"""

DEPTHS = ["Depth 0 (Context level):\n"+DEPTH_0, "Depth 1 (Containers level):\n"+DEPTH_1, "Depth 2 (Components Level):\n"+DEPTH_2]
