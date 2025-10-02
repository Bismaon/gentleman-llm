Classification of every function in the file:

1. main – 5. Controller  
   High-level orchestrator: fans-out to parsers, file-system helpers, DB helpers, refactor_faculties, store_data, log_insertion_details.

2. store_data – 6. Data-access / repository  
   Drops/inserts into three MongoDB collections; all I/O is DB I/O.

3. log_insertion_details – 4. I/O function  
   Writes informational messages to the logger (external I/O).

4. find_in_sorted_list – 3. Pure utility  
   Deterministic binary-search helper; no side effects, no I/O.

5. refactor_faculties – 3. Pure utility  
   Pure data transformation: restructures nested dicts/lists, calls only other pure helpers (find_in_sorted_list, readImportLinks).

6. readImportLinks – 4. I/O function  
   Reads every file in given directories and parses their contents; returns aggregated data.

7. (module-level) – 7. API endpoint / CLI entry-point  
   The `if __name__ == "__main__":` block is the CLI entry point; it builds the argument parser, sets up logging, and calls main.