"""LLM provider implementations."""

import re

from codeact.interfaces.agent import AgentHistoryEntry
from codeact.interfaces.llm import ILLMOutputParser, ILLMProvider, ParsedLLMOutput


class MockLLMProvider(ILLMProvider):
    """Mock implementation of the LLM provider interface."""

    def __init__(self) -> None:
        self._turn_counter = 0

    def generate(self, prompt: str, history: list[AgentHistoryEntry]) -> str:
        """Simulates LLM generating thought, action, or response."""
        # In a real scenario, history would be formatted and included in the prompt.
        print("\n--- LLM Generating ---")
        print(f"Prompt context (last observation):\n{prompt}")
        print(f"History length: {len(history)}")
        # Example logic: First turn, try code; second, give solution.
        # This logic now relies on the turn counter within the main controller,
        # but for a simple mock, we use internal state.
        last_observation = prompt  # Simplified assumption

        if "initial instruction" in last_observation and self._turn_counter == 0:
            self._turn_counter += 1
            response = """<thought>
This is turn 1. I should execute a simple Python script to check the environment.
</thought>
<execute>
import sys
import platform
py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
os_info = platform.system()
print(f"Environment Check: Python={py_version}, OS={os_info}")
result = 2 * 3
print(f"Simple Calculation: 2 * 3 = {result}")
</execute>"""
            print(f"Mock LLM Output (Turn {self._turn_counter}):\n{response}")
            return response
        elif "Environment Check" in last_observation and self._turn_counter == 1:
            self._turn_counter += 1
            response = """<thought>
This is turn 2. The code executed successfully in the previous turn.
I should now provide the final answer based on the results and the initial (mocked) request.
</thought>
<solution>
Environment tested successfully. Python version seems adequate and calculations work.
</solution>"""
            print(f"Mock LLM Output (Turn {self._turn_counter}):\n{response}")
            return response
        else:
            # Default fallback
            response = "<solution>I seem to be stuck or the request was unclear.</solution>"
            print(f"Mock LLM Output (Fallback):\n{response}")
            return response


class RegexLLMOutputParser(ILLMOutputParser):
    """Parses LLM output using regular expressions."""

    # Simple regex to find content within tags. Robust parsing might need more.
    THOUGHT_RE = re.compile(r"<thought>(.*?)</thought>", re.DOTALL | re.IGNORECASE)
    EXECUTE_RE = re.compile(r"<execute>(.*?)</execute>", re.DOTALL | re.IGNORECASE)
    SOLUTION_RE = re.compile(r"<solution>(.*?)</solution>", re.DOTALL | re.IGNORECASE)

    def parse(self, llm_output: str) -> ParsedLLMOutput:
        """Parses the LLM's raw string into structured components."""
        thought_match = self.THOUGHT_RE.search(llm_output)
        execute_match = self.EXECUTE_RE.search(llm_output)
        solution_match = self.SOLUTION_RE.search(llm_output)

        thought = thought_match.group(1).strip() if thought_match else None
        code_action = execute_match.group(1).strip() if execute_match else None
        solution = solution_match.group(1).strip() if solution_match else None

        # Basic fallback: if no action/solution tag, assume the whole thing is a solution
        # This might need refinement based on expected LLM behavior
        if not code_action and not solution and not thought:
            solution = llm_output.strip()

        return {
            "thought": thought,
            "code_action": code_action,
            "solution": solution,
            "raw_response": llm_output,
        }
