"""Agent state implementations."""


from codeact.interfaces.agent import AgentHistoryEntry, IAgentState


class InMemoryAgentState(IAgentState):
    """Simple in-memory implementation of agent state."""

    def __init__(self) -> None:
        self._history: list[AgentHistoryEntry] = []

    def add_entry(self, role: str, content: str) -> None:
        """Adds an entry to the history."""
        self._history.append({"role": role, "content": content})
        print(f"State Update: Added [{role}]")  # Logging

    def get_history(self) -> list[AgentHistoryEntry]:
        """Retrieves the full conversation history."""
        return self._history.copy()  # Return a copy to prevent external modification

    def clear_history(self) -> None:
        """Clears the agent's history."""
        self._history = []
        print("State Update: History Cleared")  # Logging
