"""Research interface definitions for web-based research capabilities."""

from typing import Protocol, TypedDict, List, Optional


class WebPage(TypedDict):
    """Structure for web page content."""

    url: str
    title: str
    content: str
    links: List[str]


class ResearchResult(TypedDict):
    """Structure for research execution results."""

    success: bool
    pages_visited: List[str]
    current_page: Optional[WebPage]
    extracted_info: str
    error_message: Optional[str]


class IResearchEnvironment(Protocol):
    """Interface for performing web-based research."""

    def navigate(self, url: str) -> ResearchResult:
        """Navigate to a specific URL."""
        ...

    def search(self, query: str) -> ResearchResult:
        """Perform a web search with the given query."""
        ...

    def extract_info(self, selector: str) -> ResearchResult:
        """Extract specific information from the current page."""
        ...

    def follow_link(self, link_text: str) -> ResearchResult:
        """Follow a link on the current page."""
        ...

    def execute_research_plan(self, plan: str) -> ResearchResult:
        """Execute a multi-step research plan described in natural language."""
        ...
