FUNCTION_TYPES_GUIDE = """
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

4. I/O functions:
   - interact with files, sockets, HTTP, DB
   - params: url/path/socket/db handle
   - return data or status
   - names like read, write, save

5. Controllers:
   - high fan-out, compose other functionss
   - params: request context, input
   - returns HTML/JSON/status or None (side effects)

6. Data access / repository:
   - SQL/ORM/cache calls
   - params: identifier, session
   - returns query result or status
   - names like get_*_by, insert, delete, update

7. API endpoints / handlers / CLIs:
   - entry points, req/ctx object or CLI args
   - returns HTTP response or exit code/output
   - often named main()

8. Event/callback/listener:
   - async event-based
   - params: event obj, optional args
   - often no return or status indicator

9. Recursion / DP:
   - calls itself
   - params: size/index/state
   - returns solution (number, list, bool)

10. Concurrency/async:
   - use threads, locks, async/await
   - params: file/url/tasks
   - returns async result (future/task)

11. Tests:
   - assert conditions
   - usually no params
   - no return except error
   - names usually start with test_ or end with _test

12. Helpers:
   - small reusable extraction or pattern functions
   - input data → output cleaned structure
"""
