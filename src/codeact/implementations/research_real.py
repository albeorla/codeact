"""Real browser-use implementation of the research environment interface."""

import asyncio
from typing import List, Optional, Any, Dict

from browser_use import Agent as BrowserAgent
from langchain.schema import HumanMessage
from codeact.interfaces.llm import ILLMProvider
from codeact.interfaces.research import IResearchEnvironment, ResearchResult, WebPage


class RealBrowserUseResearchEnvironment(IResearchEnvironment):
    """Implementation of research environment using the browser-use library."""
    
    def __init__(self, llm_provider: ILLMProvider):
        """Initialize with an LLM provider for research tasks."""
        self._llm_provider = llm_provider
        self._browser_agent = None
        self._current_page: Optional[WebPage] = None
        self._pages_visited: List[str] = []
        self._research_history: List[Dict[str, Any]] = []
        
    async def _setup_browser_agent(self, task: str):
        """Set up the browser-use agent if not already initialized."""
        if self._browser_agent is None:
            # Initialize the browser-use Agent with the LLM provider
            self._browser_agent = BrowserAgent(
                task=task,
                llm=self._llm_provider
            )
            
    def _create_research_result(self, 
                               success: bool, 
                               extracted_info: str = "", 
                               error_message: Optional[str] = None) -> ResearchResult:
        """Create a research result structure."""
        return {
            "success": success,
            "pages_visited": self._pages_visited,
            "current_page": self._current_page,
            "extracted_info": extracted_info,
            "error_message": error_message
        }
    
    def navigate(self, url: str) -> ResearchResult:
        """Navigate to a specific URL."""
        try:
            # Create a navigation task
            task = f"Navigate to {url} and summarize the page content."
            
            # Set up the browser agent and execute the task
            asyncio.run(self._setup_browser_agent(task))
            result = asyncio.run(self._browser_agent.run())
            
            # Extract page information from the result
            # The actual structure of the result will depend on browser-use's output format
            page_title = "Unknown"
            page_content = ""
            page_links = []
            
            # Try to extract information from the result
            if isinstance(result, dict):
                if "title" in result:
                    page_title = result["title"]
                if "content" in result:
                    page_content = result["content"]
                if "links" in result and isinstance(result["links"], list):
                    page_links = result["links"]
                    
            # Update state
            self._pages_visited.append(url)
            self._current_page = {
                "url": url,
                "title": page_title,
                "content": page_content,
                "links": page_links
            }
            
            # Extract summary from result
            summary = ""
            if isinstance(result, dict) and "summary" in result:
                summary = result["summary"]
            elif isinstance(result, str):
                summary = result
                
            return self._create_research_result(True, summary)
        except Exception as e:
            return self._create_research_result(False, error_message=str(e))
    
    def search(self, query: str) -> ResearchResult:
        """Perform a web search with the given query."""
        try:
            # Create a search task
            task = f"Search for '{query}' and summarize the top results."
            
            # Set up the browser agent and execute the task
            asyncio.run(self._setup_browser_agent(task))
            result = asyncio.run(self._browser_agent.run())
            
            # Update state
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            self._pages_visited.append(search_url)
            
            # Extract summary from result
            summary = ""
            if isinstance(result, dict) and "summary" in result:
                summary = result["summary"]
            elif isinstance(result, str):
                summary = result
                
            return self._create_research_result(True, summary)
        except Exception as e:
            return self._create_research_result(False, error_message=str(e))
    
    def extract_info(self, selector: str) -> ResearchResult:
        """Extract specific information from the current page."""
        if not self._current_page:
            return self._create_research_result(False, error_message="No current page to extract from")
        
        try:
            # Create an extraction task
            task = f"Extract information matching '{selector}' from the current page."
            
            # Set up the browser agent and execute the task
            asyncio.run(self._setup_browser_agent(task))
            result = asyncio.run(self._browser_agent.run())
            
            # Extract information from result
            extracted_info = ""
            if isinstance(result, dict) and "extracted_info" in result:
                extracted_info = result["extracted_info"]
            elif isinstance(result, str):
                extracted_info = result
                
            return self._create_research_result(True, extracted_info)
        except Exception as e:
            return self._create_research_result(False, error_message=str(e))
    
    def follow_link(self, link_text: str) -> ResearchResult:
        """Follow a link on the current page."""
        if not self._current_page:
            return self._create_research_result(False, error_message="No current page to navigate from")
        
        try:
            # Create a link-following task
            task = f"Find and click on a link containing '{link_text}', then summarize the new page."
            
            # Set up the browser agent and execute the task
            asyncio.run(self._setup_browser_agent(task))
            result = asyncio.run(self._browser_agent.run())
            
            # Extract page information from the result
            new_url = "Unknown URL"
            page_title = "Unknown"
            page_content = ""
            page_links = []
            
            # Try to extract information from the result
            if isinstance(result, dict):
                if "url" in result:
                    new_url = result["url"]
                if "title" in result:
                    page_title = result["title"]
                if "content" in result:
                    page_content = result["content"]
                if "links" in result and isinstance(result["links"], list):
                    page_links = result["links"]
            
            # Update state
            self._pages_visited.append(new_url)
            self._current_page = {
                "url": new_url,
                "title": page_title,
                "content": page_content,
                "links": page_links
            }
            
            # Extract summary from result
            summary = ""
            if isinstance(result, dict) and "summary" in result:
                summary = result["summary"]
            elif isinstance(result, str):
                summary = result
                
            return self._create_research_result(True, summary)
        except Exception as e:
            return self._create_research_result(False, error_message=str(e))
    
    def execute_research_plan(self, plan: str) -> ResearchResult:
        """Execute a multi-step research plan described in natural language."""
        try:
            # Use the plan directly as the task for the browser agent
            task = plan
            
            # Set up the browser agent and execute the task
            asyncio.run(self._setup_browser_agent(task))
            result = asyncio.run(self._browser_agent.run())
            
            # Extract research findings from result
            research_findings = ""
            if isinstance(result, dict):
                if "research_findings" in result:
                    research_findings = result["research_findings"]
                elif "summary" in result:
                    research_findings = result["summary"]
                
                # Update pages visited if available
                if "pages_visited" in result and isinstance(result["pages_visited"], list):
                    self._pages_visited.extend(result["pages_visited"])
            elif isinstance(result, str):
                research_findings = result
            
            return self._create_research_result(True, research_findings)
        except Exception as e:
            return self._create_research_result(False, error_message=str(e))
