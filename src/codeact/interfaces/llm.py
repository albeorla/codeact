"""LLM provider interface definitions."""

from typing import Protocol, TypedDict

from .agent import AgentHistoryEntry


class ParsedLLMOutput(TypedDict):
    """Structure for the parsed output from the LLM."""

    thought: str | None
    code_action: str | None
    solution: str | None
    raw_response: str  # Keep the original response


class ILLMProvider(Protocol):
    """Interface for interacting with a Large Language Model."""

    def generate(self, prompt: str, history: list[AgentHistoryEntry]) -> str:
        """Generates a response from the LLM based on prompt and history."""
        ...


class ILLMOutputParser(Protocol):
    """Interface for parsing the raw output string from an LLM."""

    def parse(self, llm_output: str) -> ParsedLLMOutput:
        """Parses the LLM's raw string into structured components."""
        ...
