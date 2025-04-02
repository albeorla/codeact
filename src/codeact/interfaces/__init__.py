"""Protocol interfaces for the CodeAct framework."""

from .agent import AgentHistoryEntry, IAgentState
from .execution import ExecutionResult, IExecutionEnvironment
from .llm import ILLMOutputParser, ILLMProvider, ParsedLLMOutput

__all__ = [
    "IAgentState",
    "AgentHistoryEntry",
    "ILLMProvider",
    "ILLMOutputParser",
    "ParsedLLMOutput",
    "IExecutionEnvironment",
    "ExecutionResult",
]
