"""Unit tests for the extended parser with research action recognition."""

import unittest

from codeact.implementations.parser_extended import ResearchAwareOutputParser


class TestResearchAwareOutputParser(unittest.TestCase):
    """Test cases for the research-aware output parser."""

    def setUp(self):
        """Set up the test environment."""
        self.parser = ResearchAwareOutputParser()

    def test_parse_thought(self):
        """Test parsing a thought."""
        llm_output = "<thought>I need to research quantum computing</thought>"
        result = self.parser.parse(llm_output)
        
        self.assertEqual(result["thought"], "I need to research quantum computing")
        self.assertIsNone(result["code_action"])
        self.assertIsNone(result["solution"])
        self.assertIsNone(result["research_plan"])
        self.assertIsNone(result["search_query"])
        self.assertIsNone(result["navigate_url"])

    def test_parse_research_plan(self):
        """Test parsing a research plan."""
        llm_output = """<thought>I need to research quantum computing</thought>
        <research>
        1. Search for recent advances in quantum computing
        2. Find information about quantum supremacy
        3. Look for practical applications of quantum computing
        </research>"""
        
        result = self.parser.parse(llm_output)
        
        self.assertEqual(result["thought"], "I need to research quantum computing")
        self.assertIsNone(result["code_action"])
        self.assertIsNone(result["solution"])
        self.assertEqual(result["research_plan"].strip(), """1. Search for recent advances in quantum computing
        2. Find information about quantum supremacy
        3. Look for practical applications of quantum computing""")
        self.assertIsNone(result["search_query"])
        self.assertIsNone(result["navigate_url"])

    def test_parse_search_query(self):
        """Test parsing a search query."""
        llm_output = """<thought>I need to find information about quantum computing</thought>
        <search>recent advances in quantum computing 2025</search>"""
        
        result = self.parser.parse(llm_output)
        
        self.assertEqual(result["thought"], "I need to find information about quantum computing")
        self.assertIsNone(result["code_action"])
        self.assertIsNone(result["solution"])
        self.assertIsNone(result["research_plan"])
        self.assertEqual(result["search_query"], "recent advances in quantum computing 2025")
        self.assertIsNone(result["navigate_url"])

    def test_parse_navigate_url(self):
        """Test parsing a navigation URL."""
        llm_output = """<thought>I should check the official quantum computing documentation</thought>
        <navigate>https://quantum-computing.org/docs</navigate>"""
        
        result = self.parser.parse(llm_output)
        
        self.assertEqual(result["thought"], "I should check the official quantum computing documentation")
        self.assertIsNone(result["code_action"])
        self.assertIsNone(result["solution"])
        self.assertIsNone(result["research_plan"])
        self.assertIsNone(result["search_query"])
        self.assertEqual(result["navigate_url"], "https://quantum-computing.org/docs")

    def test_parse_code_action(self):
        """Test parsing a code action."""
        llm_output = """<thought>I'll write code to analyze quantum computing data</thought>
        <execute>
        import numpy as np
        
        def analyze_quantum_data(data):
            return np.mean(data)
            
        test_data = [1, 2, 3, 4, 5]
        result = analyze_quantum_data(test_data)
        print(f"Analysis result: {result}")
        </execute>"""
        
        result = self.parser.parse(llm_output)
        
        self.assertEqual(result["thought"], "I'll write code to analyze quantum computing data")
        self.assertIsNotNone(result["code_action"])
        self.assertIn("analyze_quantum_data", result["code_action"])
        self.assertIsNone(result["solution"])
        self.assertIsNone(result["research_plan"])
        self.assertIsNone(result["search_query"])
        self.assertIsNone(result["navigate_url"])

    def test_parse_solution(self):
        """Test parsing a solution."""
        llm_output = """<thought>Based on my research, I can provide a conclusion</thought>
        <solution>
        Quantum computing has made significant advances in 2025, with practical applications
        in cryptography, drug discovery, and optimization problems.
        </solution>"""
        
        result = self.parser.parse(llm_output)
        
        self.assertEqual(result["thought"], "Based on my research, I can provide a conclusion")
        self.assertIsNone(result["code_action"])
        self.assertIsNotNone(result["solution"])
        self.assertIn("Quantum computing has made significant advances", result["solution"])
        self.assertIsNone(result["research_plan"])
        self.assertIsNone(result["search_query"])
        self.assertIsNone(result["navigate_url"])

    def test_parse_multiple_actions(self):
        """Test parsing multiple actions (should prioritize appropriately)."""
        llm_output = """<thought>I need to research and then write code</thought>
        <search>quantum computing algorithms</search>
        <execute>print("This is a code action")</execute>"""
        
        result = self.parser.parse(llm_output)
        
        self.assertEqual(result["thought"], "I need to research and then write code")
        self.assertIsNotNone(result["code_action"])
        self.assertIsNone(result["solution"])
        self.assertIsNone(result["research_plan"])
        self.assertEqual(result["search_query"], "quantum computing algorithms")
        self.assertIsNone(result["navigate_url"])


if __name__ == "__main__":
    unittest.main()
