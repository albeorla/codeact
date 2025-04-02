"""Code execution implementations."""

import contextlib
import io
import traceback
from typing import Any

from codeact.interfaces.execution import ExecutionResult, IExecutionEnvironment


class MockExecutionEnvironment(IExecutionEnvironment):
    """
    Mock implementation of the execution environment interface.
    WARNING: Uses `exec`, which is inherently insecure.
             A real implementation MUST use proper sandboxing.
    """

    def __init__(self) -> None:
        # Define available tools (functions) here for the 'exec' scope
        self._available_tools: dict[str, Any] = {"simple_math_tool": lambda x, y: x + y}
        print("Mock Execution Environment Initialized.")
        print(f"Available tools: {list(self._available_tools.keys())}")

    def execute_code(self, code_string: str) -> ExecutionResult:
        """
        Executes the code using `exec`. Not safe for untrusted code.
        """
        print(f"\n--- Mock Executing Code ---\n{code_string}\n---------------------------")
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        success = False
        local_scope = self._available_tools.copy()  # Scope for exec

        try:
            # Redirect stdout and stderr to capture output
            with contextlib.redirect_stdout(stdout_capture):
                with contextlib.redirect_stderr(stderr_capture):
                    # *** UNSAFE EXECUTION ***
                    exec(code_string, {"__builtins__": __builtins__}, local_scope)
            stdout = stdout_capture.getvalue()
            stderr = stderr_capture.getvalue()
            success = True  # No exception means success for this mock
            print("--- Mock Execution Result ---")
            if stdout:
                print(f"STDOUT:\n{stdout}")
            if stderr:
                print(f"STDERR:\n{stderr}")
            print("-----------------------------")
        except Exception:
            # Capture exception traceback into stderr
            stderr = stderr_capture.getvalue() + "\n" + traceback.format_exc()
            stdout = stdout_capture.getvalue()  # Get any stdout before the error
            success = False
            print(f"--- Mock Execution Error ---\n{stderr}\n--------------------------")

        return {"stdout": stdout, "stderr": stderr, "success": success}
