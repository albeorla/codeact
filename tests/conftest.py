"""Pytest configuration file."""

import pytest
from codeact.implementations.agent import InMemoryAgentState
from codeact.implementations.execution import MockExecutionEnvironment
from codeact.implementations.llm import MockLLMProvider, RegexLLMOutputParser
from codeact.main import AgentConfig, AgentDependencies, CodeActAgentController


@pytest.fixture
def agent_state():
    """Fixture for creating an InMemoryAgentState instance."""
    return InMemoryAgentState()


@pytest.fixture
def llm_provider():
    """Fixture for creating a MockLLMProvider instance."""
    return MockLLMProvider()


@pytest.fixture
def llm_parser():
    """Fixture for creating a RegexLLMOutputParser instance."""
    return RegexLLMOutputParser()


@pytest.fixture
def execution_environment():
    """Fixture for creating a MockExecutionEnvironment instance."""
    return MockExecutionEnvironment()


@pytest.fixture
def agent_controller(agent_state, llm_provider, llm_parser, execution_environment):
    """Fixture for creating a CodeActAgentController instance."""
    agent_config = AgentConfig(max_turns=3)
    agent_deps = AgentDependencies(
        llm_provider=llm_provider,
        exec_env=execution_environment,
        parser=llm_parser,
        agent_state=agent_state,
    )
    return CodeActAgentController(deps=agent_deps, config=agent_config)
