"""Tests for the agent state implementation."""

from codeact.implementations.agent import InMemoryAgentState


def test_in_memory_agent_state_initialization():
    """Test that the InMemoryAgentState initializes correctly."""
    state = InMemoryAgentState()
    assert state.get_history() == []


def test_in_memory_agent_state_add_entry():
    """Test that entries can be added to the agent state."""
    state = InMemoryAgentState()
    state.add_entry("user", "Hello")
    history = state.get_history()
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"


def test_in_memory_agent_state_clear_history():
    """Test that the history can be cleared."""
    state = InMemoryAgentState()
    state.add_entry("user", "Hello")
    state.clear_history()
    assert state.get_history() == []


def test_in_memory_agent_state_get_history_returns_copy():
    """Test that get_history returns a copy of the history."""
    state = InMemoryAgentState()
    state.add_entry("user", "Hello")
    history = state.get_history()
    history.append({"role": "assistant", "content": "World"})
    assert len(state.get_history()) == 1  # Original history should be unchanged
