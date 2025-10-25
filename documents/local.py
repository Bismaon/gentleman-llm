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
9. Each reasoning must explicitly state the main evidence for the chosen function_type
   using one of these patterns:
   - "classified as <type> because it [core behavior]"
   - "fits the <type> type since it [reason]"
   This ensures consistent phrasing and easier parsing.

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
"""

HIERARCHY_NOTE = """
Prompt precedence order (highest to lowest):
1. FUNCTION_TYPES guide — the definitive taxonomy for function_type labels.
2. RULES — governs format and schema.
3. DEPTH prompt — only controls *detail level*, not label meaning.
4. THINKING_STEPS — reasoning outline, not structural output.
Never invent function_type labels beyond FUNCTION_TYPES.
"""

DEPTH_0 = """
Depth 0 (Context level):
Classify each function only by its broad conceptual role.
- Output strictly follows schema.
- Use FUNCTION_TYPES only.
- Provide one-sentence reasoning.
"""
DEPTH_1 = DEPTH_0 + """
Depth 1 adds operational context:
- Refine descriptions and reasoning to mention external interactions or data flow.
- Keep function_type identical to Depth 0 unless strong evidence suggests otherwise.
"""
DEPTH_2 = DEPTH_1 + """
Depth 2 adds relationships:
- Include relations (calls, called_by, dependencies).
- Never alter function_type decided in previous depth; refine reasoning only.
"""

DEPTHS = [DEPTH_0, DEPTH_1, DEPTH_2]
