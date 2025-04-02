"""Agent state interface definitions."""

from typing import Protocol, TypedDict


class AgentHistoryEntry(TypedDict):
    """Structure for a single entry in the agent's history."""

    role: str
    content: str


class IAgentState(Protocol):
    """Interface for managing the agent's state and history."""

    def add_entry(self, role: str, content: str) -> None:
        """Adds an entry to the history."""
        ...

    def get_history(self) -> list[AgentHistoryEntry]:
        """Retrieves the full conversation history."""
        ...

    def clear_history(self) -> None:
        """Clears the agent's history."""
        ...
