"""Unit tests for the research interface."""

import unittest
from typing import Dict, List, Optional

from codeact.interfaces.research import IResearchEnvironment, ResearchResult, WebPage


class TestResearchInterface(unittest.TestCase):
    """Test cases for the research interface."""

    def test_research_result_structure(self):
        """Test that ResearchResult TypedDict has the expected structure."""
        # Create a minimal valid ResearchResult
        result: ResearchResult = {
            "success": True,
            "pages_visited": ["https://example.com"],
            "current_page": None,
            "extracted_info": "Test info",
            "error_message": None
        }
        
        # Verify the structure
        self.assertIsInstance(result["success"], bool)
        self.assertIsInstance(result["pages_visited"], list)
        self.assertIsNone(result["current_page"])
        self.assertIsInstance(result["extracted_info"], str)
        self.assertIsNone(result["error_message"])

    def test_web_page_structure(self):
        """Test that WebPage TypedDict has the expected structure."""
        # Create a valid WebPage
        page: WebPage = {
            "url": "https://example.com",
            "title": "Example Page",
            "content": "This is an example page.",
            "links": ["https://example.com/link1", "https://example.com/link2"]
        }
        
        # Verify the structure
        self.assertIsInstance(page["url"], str)
        self.assertIsInstance(page["title"], str)
        self.assertIsInstance(page["content"], str)
        self.assertIsInstance(page["links"], list)
        self.assertIsInstance(page["links"][0], str)


class MockResearchEnvironment(IResearchEnvironment):
    """Mock implementation of IResearchEnvironment for testing."""
    
    def __init__(self):
        self.current_page: Optional[WebPage] = None
        self.pages_visited: List[str] = []
    
    def navigate(self, url: str) -> ResearchResult:
        """Navigate to a specific URL."""
        self.pages_visited.append(url)
        self.current_page = {
            "url": url,
            "title": f"Title of {url}",
            "content": f"Content of {url}",
            "links": [f"{url}/link1", f"{url}/link2"]
        }
        return {
            "success": True,
            "pages_visited": self.pages_visited,
            "current_page": self.current_page,
            "extracted_info": f"Information from {url}",
            "error_message": None
        }
    
    def search(self, query: str) -> ResearchResult:
        """Perform a web search with the given query."""
        url = f"https://search.example.com?q={query}"
        self.pages_visited.append(url)
        self.current_page = {
            "url": url,
            "title": f"Search results for {query}",
            "content": f"Search results content for {query}",
            "links": [f"https://result1.example.com?q={query}", f"https://result2.example.com?q={query}"]
        }
        return {
            "success": True,
            "pages_visited": self.pages_visited,
            "current_page": self.current_page,
            "extracted_info": f"Search results for {query}",
            "error_message": None
        }
    
    def extract_info(self, selector: str) -> ResearchResult:
        """Extract specific information from the current page."""
        if not self.current_page:
            return {
                "success": False,
                "pages_visited": self.pages_visited,
                "current_page": None,
                "extracted_info": "",
                "error_message": "No current page to extract from"
            }
        
        return {
            "success": True,
            "pages_visited": self.pages_visited,
            "current_page": self.current_page,
            "extracted_info": f"Extracted {selector} from {self.current_page['url']}",
            "error_message": None
        }
    
    def follow_link(self, link_text: str) -> ResearchResult:
        """Follow a link on the current page."""
        if not self.current_page:
            return {
                "success": False,
                "pages_visited": self.pages_visited,
                "current_page": None,
                "extracted_info": "",
                "error_message": "No current page to navigate from"
            }
        
        new_url = f"{self.current_page['url']}/{link_text.lower().replace(' ', '-')}"
        self.pages_visited.append(new_url)
        self.current_page = {
            "url": new_url,
            "title": f"Page about {link_text}",
            "content": f"Content about {link_text}",
            "links": [f"{new_url}/sublink1", f"{new_url}/sublink2"]
        }
        
        return {
            "success": True,
            "pages_visited": self.pages_visited,
            "current_page": self.current_page,
            "extracted_info": f"Followed link to {new_url}",
            "error_message": None
        }
    
    def execute_research_plan(self, plan: str) -> ResearchResult:
        """Execute a multi-step research plan described in natural language."""
        # Simulate executing a research plan
        self.pages_visited.append("https://plan.example.com/step1")
        self.pages_visited.append("https://plan.example.com/step2")
        
        self.current_page = {
            "url": "https://plan.example.com/final",
            "title": "Research Plan Results",
            "content": f"Results of research plan: {plan}",
            "links": ["https://plan.example.com/related1", "https://plan.example.com/related2"]
        }
        
        return {
            "success": True,
            "pages_visited": self.pages_visited,
            "current_page": self.current_page,
            "extracted_info": f"Research findings for plan: {plan}\n1. Finding 1\n2. Finding 2",
            "error_message": None
        }


class TestMockResearchEnvironment(unittest.TestCase):
    """Test cases for the mock research environment implementation."""
    
    def setUp(self):
        """Set up the test environment."""
        self.research_env = MockResearchEnvironment()
    
    def test_navigate(self):
        """Test navigation functionality."""
        result = self.research_env.navigate("https://example.com")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["current_page"]["url"], "https://example.com")
        self.assertIn("https://example.com", result["pages_visited"])
        self.assertIsNotNone(result["extracted_info"])
    
    def test_search(self):
        """Test search functionality."""
        result = self.research_env.search("test query")
        
        self.assertTrue(result["success"])
        self.assertIn("test query", result["current_page"]["title"])
        self.assertIn("https://search.example.com?q=test query", result["pages_visited"])
        self.assertIsNotNone(result["extracted_info"])
    
    def test_extract_info_with_page(self):
        """Test extracting information with a current page."""
        # First navigate to set a current page
        self.research_env.navigate("https://example.com")
        
        # Then extract info
        result = self.research_env.extract_info("test selector")
        
        self.assertTrue(result["success"])
        self.assertIn("test selector", result["extracted_info"])
        self.assertIsNotNone(result["current_page"])
    
    def test_extract_info_without_page(self):
        """Test extracting information without a current page."""
        # Create a fresh environment with no current page
        env = MockResearchEnvironment()
        
        # Try to extract info
        result = env.extract_info("test selector")
        
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error_message"])
    
    def test_follow_link_with_page(self):
        """Test following a link with a current page."""
        # First navigate to set a current page
        self.research_env.navigate("https://example.com")
        
        # Then follow a link
        result = self.research_env.follow_link("Test Link")
        
        self.assertTrue(result["success"])
        self.assertIn("test-link", result["current_page"]["url"])
        self.assertEqual(len(result["pages_visited"]), 2)
    
    def test_follow_link_without_page(self):
        """Test following a link without a current page."""
        # Create a fresh environment with no current page
        env = MockResearchEnvironment()
        
        # Try to follow a link
        result = env.follow_link("Test Link")
        
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["error_message"])
    
    def test_execute_research_plan(self):
        """Test executing a research plan."""
        result = self.research_env.execute_research_plan("Find information about X")
        
        self.assertTrue(result["success"])
        self.assertGreaterEqual(len(result["pages_visited"]), 2)
        self.assertIn("Research findings", result["extracted_info"])
        self.assertEqual(result["current_page"]["url"], "https://plan.example.com/final")


if __name__ == "__main__":
    unittest.main()
