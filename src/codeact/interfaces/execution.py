"""Code execution interface definitions."""

from typing import Protocol, TypedDict


class ExecutionResult(TypedDict):
    """Structure for code execution results."""

    stdout: str
    stderr: str
    success: bool  # Indicates if execution completed without exceptions


class IExecutionEnvironment(Protocol):
    """Interface for executing code safely."""

    def execute_code(self, code_string: str) -> ExecutionResult:
        """Executes the provided code string and returns results."""
        ...
