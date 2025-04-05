"""Unit tests for the research-enabled agent controller."""

import unittest
from unittest.mock import MagicMock, patch

from codeact.interfaces.agent import IAgentState
from codeact.interfaces.execution import IExecutionEnvironment
from codeact.interfaces.llm import ILLMProvider, ILLMOutputParser
from codeact.interfaces.research import IResearchEnvironment
from codeact.main_extended import ResearchEnabledAgentController, ExtendedAgentDependencies, ExtendedAgentConfig


class TestResearchEnabledAgentController(unittest.TestCase):
    """Test cases for the research-enabled agent controller."""

    def setUp(self):
        """Set up the test environment with mocked dependencies."""
        # Create mock dependencies
        self.mock_llm = MagicMock(spec=ILLMProvider)
        self.mock_exec_env = MagicMock(spec=IExecutionEnvironment)
        self.mock_parser = MagicMock(spec=ILLMOutputParser)
        self.mock_agent_state = MagicMock(spec=IAgentState)
        self.mock_research_env = MagicMock(spec=IResearchEnvironment)
        
        # Configure mock behavior
        self.mock_agent_state.get_history.return_value = []
        
        # Create dependencies container
        self.deps = ExtendedAgentDependencies(
            llm_provider=self.mock_llm,
            exec_env=self.mock_exec_env,
            parser=self.mock_parser,
            agent_state=self.mock_agent_state,
            research_env=self.mock_research_env
        )
        
        # Create config
        self.config = ExtendedAgentConfig(
            max_turns=3,
            enable_research=True,
            research_timeout=60,
            max_pages_per_task=5
        )
        
        # Create controller
        self.controller = ResearchEnabledAgentController(self.deps, self.config)

    def test_initialization(self):
        """Test that the controller initializes correctly."""
        # Verify that the controller has the expected attributes
        self.assertEqual(self.controller._max_turns, 3)
        self.assertTrue(hasattr(self.controller, '_research_env'))
        self.assertTrue(hasattr(self.controller, '_extended_config'))
        self.assertTrue(self.controller._extended_config.enable_research)

    def test_create_research_observation(self):
        """Test creating an observation string from research results."""
        # Create a sample research result
        research_result = {
            "success": True,
            "pages_visited": ["https://example.com", "https://example.org"],
            "current_page": {
                "url": "https://example.org",
                "title": "Example Page",
                "content": "Example content",
                "links": ["https://example.org/link1"]
            },
            "extracted_info": "Important information extracted from the page.",
            "error_message": None
        }
        
        # Call the method
        observation = self.controller._create_research_observation(research_result)
        
        # Verify the observation
        self.assertIn("Research task completed successfully", observation)
        self.assertIn("Important information extracted", observation)
        self.assertIn("https://example.com", observation)
        self.assertIn("https://example.org", observation)
        self.assertIn("Current page: https://example.org", observation)

    def test_run_interaction_with_research_plan(self):
        """Test running an interaction with a research plan."""
        # Configure mocks
        self.mock_llm.generate.return_value = "<thought>I need to research</thought><research>Research plan</research>"
        self.mock_parser.parse.return_value = {
            "thought": "I need to research",
            "code_action": None,
            "solution": None,
            "research_plan": "Research plan",
            "search_query": None,
            "navigate_url": None
        }
        self.mock_research_env.execute_research_plan.return_value = {
            "success": True,
            "pages_visited": ["https://example.com"],
            "current_page": None,
            "extracted_info": "Research findings",
            "error_message": None
        }
        
        # Run the interaction
        result, history = self.controller.run_interaction("Research quantum computing")
        
        # Verify the interaction
        self.mock_llm.generate.assert_called_once()
        self.mock_parser.parse.assert_called_once()
        self.mock_research_env.execute_research_plan.assert_called_once_with("Research plan")
        self.mock_agent_state.add_entry.assert_any_call("assistant_research", "Research plan")

    def test_run_interaction_with_search_query(self):
        """Test running an interaction with a search query."""
        # Configure mocks
        self.mock_llm.generate.return_value = "<thought>I need to search</thought><search>quantum computing</search>"
        self.mock_parser.parse.return_value = {
            "thought": "I need to search",
            "code_action": None,
            "solution": None,
            "research_plan": None,
            "search_query": "quantum computing",
            "navigate_url": None
        }
        self.mock_research_env.search.return_value = {
            "success": True,
            "pages_visited": ["https://search.example.com?q=quantum+computing"],
            "current_page": None,
            "extracted_info": "Search results",
            "error_message": None
        }
        
        # Run the interaction
        result, history = self.controller.run_interaction("Research quantum computing")
        
        # Verify the interaction
        self.mock_llm.generate.assert_called_once()
        self.mock_parser.parse.assert_called_once()
        self.mock_research_env.search.assert_called_once_with("quantum computing")
        self.mock_agent_state.add_entry.assert_any_call("assistant_search", "quantum computing")

    def test_run_interaction_with_navigate_url(self):
        """Test running an interaction with a navigate URL."""
        # Configure mocks
        self.mock_llm.generate.return_value = "<thought>I need to visit</thought><navigate>https://quantum-computing.org</navigate>"
        self.mock_parser.parse.return_value = {
            "thought": "I need to visit",
            "code_action": None,
            "solution": None,
            "research_plan": None,
            "search_query": None,
            "navigate_url": "https://quantum-computing.org"
        }
        self.mock_research_env.navigate.return_value = {
            "success": True,
            "pages_visited": ["https://quantum-computing.org"],
            "current_page": {
                "url": "https://quantum-computing.org",
                "title": "Quantum Computing",
                "content": "Information about quantum computing",
                "links": []
            },
            "extracted_info": "Page content",
            "error_message": None
        }
        
        # Run the interaction
        result, history = self.controller.run_interaction("Research quantum computing")
        
        # Verify the interaction
        self.mock_llm.generate.assert_called_once()
        self.mock_parser.parse.assert_called_once()
        self.mock_research_env.navigate.assert_called_once_with("https://quantum-computing.org")
        self.mock_agent_state.add_entry.assert_any_call("assistant_navigate", "https://quantum-computing.org")

    def test_run_interaction_with_code_action(self):
        """Test running an interaction with a code action."""
        # Configure mocks
        self.mock_llm.generate.return_value = "<thought>I need to execute code</thought><execute>print('Hello')</execute>"
        self.mock_parser.parse.return_value = {
            "thought": "I need to execute code",
            "code_action": "print('Hello')",
            "solution": None,
            "research_plan": None,
            "search_query": None,
            "navigate_url": None
        }
        self.mock_exec_env.execute_code.return_value = {
            "stdout": "Hello\n",
            "stderr": "",
            "success": True
        }
        
        # Run the interaction
        result, history = self.controller.run_interaction("Execute some code")
        
        # Verify the interaction
        self.mock_llm.generate.assert_called_once()
        self.mock_parser.parse.assert_called_once()
        self.mock_exec_env.execute_code.assert_called_once_with("print('Hello')")
        self.mock_agent_state.add_entry.assert_any_call("assistant_action", "print('Hello')")

    def test_run_interaction_with_solution(self):
        """Test running an interaction with a solution."""
        # Configure mocks
        self.mock_llm.generate.return_value = "<thought>I have the answer</thought><solution>42 is the answer</solution>"
        self.mock_parser.parse.return_value = {
            "thought": "I have the answer",
            "code_action": None,
            "solution": "42 is the answer",
            "research_plan": None,
            "search_query": None,
            "navigate_url": None
        }
        
        # Run the interaction
        result, history = self.controller.run_interaction("What is the answer?")
        
        # Verify the interaction
        self.mock_llm.generate.assert_called_once()
        self.mock_parser.parse.assert_called_once()
        self.mock_agent_state.add_entry.assert_any_call("assistant_solution", "42 is the answer")
        self.assertIn("42 is the answer", result)

    def test_run_interaction_with_research_disabled(self):
        """Test running an interaction with research disabled."""
        # Create a controller with research disabled
        config = ExtendedAgentConfig(
            max_turns=3,
            enable_research=False
        )
        controller = ResearchEnabledAgentController(self.deps, config)
        
        # Configure mocks
        self.mock_llm.generate.return_value = "<thought>I need to research</thought><research>Research plan</research>"
        self.mock_parser.parse.return_value = {
            "thought": "I need to research",
            "code_action": None,
            "solution": None,
            "research_plan": "Research plan",
            "search_query": None,
            "navigate_url": None
        }
        
        # Run the interaction
        controller.run_interaction("Research quantum computing")
        
        # Verify the research was not executed
        self.mock_research_env.execute_research_plan.assert_not_called()


if __name__ == "__main__":
    unittest.main()
