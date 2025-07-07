# Purpose: Execute Python code blocks in a controlled environment.
# Used by: Main loop in TaskSolver (core.py) when code blocks are detected.
#
# Requirements:
# - Code block is valid Python
# - System has permission to execute code
# - stdout can be captured and redirected
#
# Known issues/limitations:
# - safety_checker is a placeholder (always returns True)
# - Uses unsafe exec() without sandboxing
# - No resource limits (CPU, memory, time)
# - No protection against dangerous operations
# - No handling of state between executions
# - Global environment not cleaned between runs
# - Can interfere with main program's stdout



import sys
from io import StringIO

def safety_checker(code: str) -> bool:
    # TODO: Implement proper safety checks
    return True

def safe_execute_code(code: str) -> str:
    if not safety_checker(code):
        return "Error: Code failed safety check"

    # Capture stdout
    old_stdout = sys.stdout
    redirected_output = StringIO()
    sys.stdout = redirected_output

    try:
        # WARNING: This is unsafe and only for initial testing
        exec(code)
        output = redirected_output.getvalue()
        return output if output else "Code executed with no output"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        sys.stdout = old_stdout