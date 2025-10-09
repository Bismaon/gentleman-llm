FUNCTION_TYPES_GUIDE_BASE = """
Classify functions into one of the following categories:
1. Constructors/initializers:
   - factory functions
   - params = class params
   - returns None
   - example: __init__

2. Getters/Setters/Properties:
   - tiny, no heavy logic
   - getter: no params, returns a field
   - setter: one param, returns None
   - names like get, set, has, is, contains, len, size

3. Pure utilities:
   - no I/O
   - math/string/data transforms
   - deterministic
   - depends only on input params

4. Recursion / DP:
   - calls itself
   - params: size/index/state
   - returns solution (number, list, bool)

5. Concurrency/async:
   - use threads, locks, async/await
   - params: file/url/tasks
   - returns async result (future/task)

6. Tests:
   - assert conditions
   - usually no params
   - no return except error
   - names usually start with test_ or end with _test
"""
FUNCTION_TYPES_GUIDE_WEB = """
a. I/O functions:
   - interact with files, sockets, HTTP, DB
   - params: url/path/socket/db handle
   - return data or status
   - names like read, write, save

b. Controllers:
   - high fan-out, compose other functionss
   - params: request context, input
   - returns HTML/JSON/status or None (side effects)

c. Data access / repository:
   - SQL/ORM/cache calls
   - params: identifier, session
   - returns query result or status
   - names like get_*_by, insert, delete, update

d. API endpoints / handlers / CLIs:
   - entry points, req/ctx object or CLI args
   - returns HTTP response or exit code/output
   - often named main()

e. Event/callback/listener:
   - async event-based
   - params: event obj, optional args
   - often no return or status indicator
"""
PERSONA = """You are an expert Code Concept Modeler tasked with analyzing source code and outputting a definition file for a projectional editor (Gentleman). This output must strictly follow to the Concept Model Schema (which defines concepts, attributes, properties, and constraints).
"""

RULES = """Follow these rules strictly:
- Respond only with JSON, no explanations or natural language.  
- You must only classify functions explicitly defined in the source code. Ignore imported functions, built-in functions, and lambda functions.
- Validate your reasoning internally before answering, so the JSON is correct.  
- Do not invent fields outside the schema.  
- Do not output comments, prose, or markdown. JSON only.  
- Each function must be classified into a "Concept".  
- Descriptions in the schema are meant as snippets as to what the functionality of this code is.
- A property tag is not always required. Only include it if the function has a clear return type.
- A constraint tag is not always required. Only include it if the function has clear constraints (e.g., specific value ranges, patterns, or enumerations).
- Always output one JSON object with a top-level key concept containing an array. Do not use keys like Concept: around each element.
"""

THINKING_STEPS = """
[1. Contextual Setup and Dependencies]
1. Project Scope Overview: State the high-level goals and technologies used. This sets the stage for accurate and relevant concept generation.
2. External Relations: Describe the dependencies and interactions this model will have with any external systems or other modules. These dependencies will typically map to Attributes (extrinsic relations) or External Interfaces.
[2. Scaffold First: Structural Plan] Before defining the model structure in JSON, outline the structure using the terminology provided above.
1. Static Components First: Identify and define any constants, enumerations, or simple value restrictions. These should primarily be defined as Derivative concepts focusing on Constraints (e.g., RangeConstraint, ValuesConstraint).
2. Core Concepts and Nature: List the main concepts. For each, explicitly state its required nature (concrete, prototype, or derivative).
3. Prototype/Reusability Strategy: Identify which components or structures can be generalized for reuse as Prototype concepts (base skeletons).
4. Managing Complexity: Explain how you will use Abstraction and Encapsulation (e.g., interfaces or abstract classes) to define the most Complex interactions or highly coupled components, reducing the need for the user to understand implementation details.
[3. Detailed Concept Definition and Robustness]
1. Defining Relations: For every major concept, define its structural composition. Clearly distinguish between Attributes (extrinsic, user-defined values, possibly optional or required) and Properties (intrinsic, constant, or computed values).
2. Constraint Implementation and Error Handling: Explicitly list all possible errors or edge cases that could occur (e.g., input validation failure). Ensure that every attribute that accepts external input or relies on strict formatting has a corresponding Constraint defined (either inline or via a Derivative type) to gracefully handle unexpected inputs.
[4. Final Output Format]
Generate the complete Concept Model Definition strictly in JSON format, ensuring it adheres to the schema fields (including name, nature, attributes, properties, and constraint). Ensure the output integrates the code fragments relevant to the concepts and their context."""

DEPTH_0 = """
Provide a high-level abstraction of each function in the file using the context level of the C4 model.
- Only include the function type, its nature (must be `concrete`, `prototype`, or `derivative`), the parameters (as attributes with type) and return types.
- Do not include relations, or any internal logic.
- Output must be valid JSON following the schema
"""

DEPTH_1 = """
Provide a high-level abstraction of each function in the file using the container level of the C4 model.
- Include the function name (as one of the types of function defined), its nature (must be `concrete`, `prototype`, or `derivative`), parameters,  return type (as a property) and relations.
- Ignore constraints, and internal logic.
- Output must be valid JSON following the schema: Concept with name, nature, attributes (parameters), and properties (return type).
"""

DEPTH_2 = """
Provide a semantic and relational abstraction of each function in the file.
- Include function name (as one of the types of function defined), parameters (attributes with types and constraints if present), return type (as a property), and notable constraints (pattern, range, values, equality, match).
- Include relations to other functions or modules (calls, called_by, dependencies).
- Output must be valid JSON following the schema: Concept with name, nature, attributes, properties, constraints, and relations.
"""
DEPTHS = [DEPTH_0, DEPTH_1, DEPTH_2]
