"""Enhanced research capabilities for the browser-use integration."""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional, Tuple

from browser_use import Agent as BrowserAgent
from codeact.interfaces.llm import ILLMProvider
from codeact.interfaces.research import IResearchEnvironment, ResearchResult, WebPage
from codeact.implementations.llm_adapter import LLMProviderAdapter


class EnhancedBrowserUseResearchEnvironment(IResearchEnvironment):
    """Enhanced implementation of research environment with advanced capabilities."""
    
    def __init__(self, llm_provider: ILLMProvider):
        """Initialize with an LLM provider for research tasks."""
        self._llm_provider = llm_provider
        self._browser_agent = None
        self._current_page: Optional[WebPage] = None
        self._pages_visited: List[str] = []
        self._research_history: List[Dict[str, Any]] = []
        self._research_cache: Dict[str, Any] = {}
        self._cache_dir = os.path.join(os.getcwd(), "research_cache")
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)
    
    async def _setup_browser_agent(self, task: str):
        """Set up the browser-use agent with the given task."""
        # Create an adapter for the LLM provider
        llm_adapter = LLMProviderAdapter(self._llm_provider)
        
        # Initialize the browser-use Agent with the adapted LLM provider
        self._browser_agent = BrowserAgent(
            task=task,
            llm=llm_adapter
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
    
    def _cache_result(self, key: str, result: Any):
        """Cache a research result for future use."""
        self._research_cache[key] = result
        
        # Also save to disk for persistence
        cache_file = os.path.join(self._cache_dir, f"{key.replace('/', '_').replace(':', '_')}.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump(result, f)
        except Exception:
            # Silently fail if caching to disk fails
            pass
    
    def _get_cached_result(self, key: str) -> Optional[Any]:
        """Get a cached research result if available."""
        # First check in-memory cache
        if key in self._research_cache:
            return self._research_cache[key]
        
        # Then check disk cache
        cache_file = os.path.join(self._cache_dir, f"{key.replace('/', '_').replace(':', '_')}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    result = json.load(f)
                    self._research_cache[key] = result  # Update in-memory cache
                    return result
            except Exception:
                # Silently fail if reading from disk fails
                pass
        
        return None
    
    def navigate(self, url: str, use_cache: bool = True) -> ResearchResult:
        """
        Navigate to a specific URL.
        
        Args:
            url: The URL to navigate to
            use_cache: Whether to use cached results if available
        """
        # Check cache first if enabled
        if use_cache:
            cache_key = f"navigate_{url}"
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                # Update state from cached result
                if "current_page" in cached_result and cached_result["current_page"]:
                    self._current_page = cached_result["current_page"]
                if "pages_visited" in cached_result and url not in self._pages_visited:
                    self._pages_visited.append(url)
                return cached_result
        
        try:
            # Create a navigation task with enhanced instructions
            task = (
                f"Navigate to {url} and perform the following tasks:\n"
                f"1. Extract the page title\n"
                f"2. Extract the main content\n"
                f"3. Identify and extract all important links\n"
                f"4. Summarize the key information on the page\n"
                f"5. Extract any relevant data like dates, statistics, or key facts"
            )
            
            # Set up the browser agent and execute the task
            asyncio.run(self._setup_browser_agent(task))
            result = asyncio.run(self._browser_agent.run())
            
            # Process the result
            page_title = "Unknown"
            page_content = ""
            page_links = []
            summary = ""
            
            # Extract information from the result
            if isinstance(result, dict):
                if "title" in result:
                    page_title = result["title"]
                if "content" in result:
                    page_content = result["content"]
                if "links" in result and isinstance(result["links"], list):
                    page_links = result["links"]
                if "summary" in result:
                    summary = result["summary"]
            elif isinstance(result, str):
                # If result is a string, use it as the summary
                summary = result
                
            # Update state
            self._pages_visited.append(url)
            self._current_page = {
                "url": url,
                "title": page_title,
                "content": page_content,
                "links": page_links
            }
            
            # Create the research result
            research_result = self._create_research_result(True, summary)
            
            # Cache the result
            self._cache_result(f"navigate_{url}", research_result)
            
            return research_result
        except Exception as e:
            return self._create_research_result(False, error_message=str(e))
    
    def search(self, query: str, use_cache: bool = True) -> ResearchResult:
        """
        Perform a web search with the given query.
        
        Args:
            query: The search query
            use_cache: Whether to use cached results if available
        """
        # Check cache first if enabled
        if use_cache:
            cache_key = f"search_{query}"
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
        
        try:
            # Create a search task with enhanced instructions
            task = (
                f"Search for '{query}' and perform the following tasks:\n"
                f"1. Analyze the top search results\n"
                f"2. Extract titles and snippets from the most relevant results\n"
                f"3. Identify the most authoritative sources\n"
                f"4. Summarize the key information across all results\n"
                f"5. Note any contradictory information or different perspectives"
            )
            
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
            
            # Create the research result
            research_result = self._create_research_result(True, summary)
            
            # Cache the result
            self._cache_result(f"search_{query}", research_result)
            
            return research_result
        except Exception as e:
            return self._create_research_result(False, error_message=str(e))
    
    def extract_info(self, selector: str, use_cache: bool = True) -> ResearchResult:
        """
        Extract specific information from the current page.
        
        Args:
            selector: The selector or description of information to extract
            use_cache: Whether to use cached results if available
        """
        if not self._current_page:
            return self._create_research_result(False, error_message="No current page to extract from")
        
        # Check cache first if enabled
        if use_cache:
            cache_key = f"extract_{self._current_page['url']}_{selector}"
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
        
        try:
            # Create an extraction task with enhanced instructions
            task = (
                f"On the current page, extract information matching '{selector}' by:\n"
                f"1. Identifying all elements that match the description\n"
                f"2. Extracting the text content from these elements\n"
                f"3. Organizing the information in a structured format\n"
                f"4. Providing context for the extracted information\n"
                f"5. Summarizing the key points from the extracted information"
            )
            
            # Set up the browser agent and execute the task
            asyncio.run(self._setup_browser_agent(task))
            result = asyncio.run(self._browser_agent.run())
            
            # Extract information from result
            extracted_info = ""
            if isinstance(result, dict) and "extracted_info" in result:
                extracted_info = result["extracted_info"]
            elif isinstance(result, str):
                extracted_info = result
            
            # Create the research result
            research_result = self._create_research_result(True, extracted_info)
            
            # Cache the result
            if self._current_page and 'url' in self._current_page:
                self._cache_result(f"extract_{self._current_page['url']}_{selector}", research_result)
            
            return research_result
        except Exception as e:
            return self._create_research_result(False, error_message=str(e))
    
    def follow_link(self, link_text: str, use_cache: bool = True) -> ResearchResult:
        """
        Follow a link on the current page.
        
        Args:
            link_text: Text or description of the link to follow
            use_cache: Whether to use cached results if available
        """
        if not self._current_page:
            return self._create_research_result(False, error_message="No current page to navigate from")
        
        # Check cache first if enabled
        if use_cache:
            cache_key = f"follow_{self._current_page['url']}_{link_text}"
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                # Update state from cached result
                if "current_page" in cached_result and cached_result["current_page"]:
                    self._current_page = cached_result["current_page"]
                if "pages_visited" in cached_result and isinstance(cached_result["pages_visited"], list):
                    for url in cached_result["pages_visited"]:
                        if url not in self._pages_visited:
                            self._pages_visited.append(url)
                return cached_result
        
        try:
            # Create a link-following task with enhanced instructions
            task = (
                f"On the current page, find and click on a link containing '{link_text}', then:\n"
                f"1. Extract the URL of the new page\n"
                f"2. Extract the page title\n"
                f"3. Extract the main content\n"
                f"4. Identify and extract all important links\n"
                f"5. Summarize the key information on the new page"
            )
            
            # Set up the browser agent and execute the task
            asyncio.run(self._setup_browser_agent(task))
            result = asyncio.run(self._browser_agent.run())
            
            # Process the result
            new_url = "Unknown URL"
            page_title = "Unknown"
            page_content = ""
            page_links = []
            summary = ""
            
            # Extract information from the result
            if isinstance(result, dict):
                if "url" in result:
                    new_url = result["url"]
                if "title" in result:
                    page_title = result["title"]
                if "content" in result:
                    page_content = result["content"]
                if "links" in result and isinstance(result["links"], list):
                    page_links = result["links"]
                if "summary" in result:
                    summary = result["summary"]
            elif isinstance(result, str):
                # If result is a string, use it as the summary
                summary = result
            
            # Update state
            self._pages_visited.append(new_url)
            self._current_page = {
                "url": new_url,
                "title": page_title,
                "content": page_content,
                "links": page_links
            }
            
            # Create the research result
            research_result = self._create_research_result(True, summary)
            
            # Cache the result
            if self._current_page and 'url' in self._current_page:
                self._cache_result(f"follow_{self._current_page['url']}_{link_text}", research_result)
            
            return research_result
        except Exception as e:
            return self._create_research_result(False, error_message=str(e))
    
    def execute_research_plan(self, plan: str, use_cache: bool = True) -> ResearchResult:
        """
        Execute a multi-step research plan described in natural language.
        
        Args:
            plan: The research plan to execute
            use_cache: Whether to use cached results if available
        """
        # Check cache first if enabled
        if use_cache:
            cache_key = f"plan_{hash(plan)}"
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                # Update state from cached result
                if "current_page" in cached_result and cached_result["current_page"]:
                    self._current_page = cached_result["current_page"]
                if "pages_visited" in cached_result and isinstance(cached_result["pages_visited"], list):
                    for url in cached_result["pages_visited"]:
                        if url not in self._pages_visited:
                            self._pages_visited.append(url)
                return cached_result
        
        try:
            # Enhance the research plan with additional instructions
            enhanced_plan = (
                f"Execute the following research plan:\n\n{plan}\n\n"
                f"While executing this plan, please:\n"
                f"1. Keep track of all pages visited\n"
                f"2. Extract key information from each page\n"
                f"3. Compare and synthesize information across sources\n"
                f"4. Note any contradictions or inconsistencies\n"
                f"5. Organize findings in a structured format\n"
                f"6. Provide a comprehensive summary of all research findings"
            )
            
            # Set up the browser agent and execute the task
            asyncio.run(self._setup_browser_agent(enhanced_plan))
            result = asyncio.run(self._browser_agent.run())
            
            # Process the result
            research_findings = ""
            visited_pages = []
            
            # Extract information from the result
            if isinstance(result, dict):
                if "research_findings" in result:
                    research_findings = result["research_findings"]
                elif "summary" in result:
                    research_findings = result["summary"]
                elif "content" in result:
                    research_findings = result["content"]
                
                # Update pages visited if available
                if "pages_visited" in result and isinstance(result["pages_visited"], list):
                    visited_pages = result["pages_visited"]
            elif isinstance(result, str):
                research_findings = result
            
            # Update state
            for url in visited_pages:
                if url not in self._pages_visited:
                    self._pages_visited.append(url)
            
            # Create the research result
            research_result = self._create_research_result(True, research_findings)
            
            # Cache the result
            self._cache_result(f"plan_{hash(plan)}", research_result)
            
            return research_result
        except Exception as e:
            return self._create_research_result(False, error_message=str(e))
    
    def compare_sources(self, urls: List[str], topic: str) -> ResearchResult:
        """
        Compare information across multiple sources on a specific topic.
        
        Args:
            urls: List of URLs to compare
            topic: The topic to compare across sources
        """
        try:
            # Create a comparison task
            task = (
                f"Compare information about '{topic}' across the following sources:\n"
                f"{', '.join(urls)}\n\n"
                f"For each source:\n"
                f"1. Navigate to the URL\n"
                f"2. Extract information related to '{topic}'\n"
                f"3. Note the perspective or stance of the source\n"
                f"4. Identify key claims and supporting evidence\n\n"
                f"Then compare across sources:\n"
                f"1. Identify points of agreement\n"
                f"2. Highlight contradictions or disagreements\n"
                f"3. Assess the credibility of each source\n"
                f"4. Synthesize a balanced view of '{topic}' based on all sources"
            )
            
            # Set up the browser agent and execute the task
            asyncio.run(self._setup_browser_agent(task))
            result = asyncio.run(self._browser_agent.run())
            
            # Process the result
            comparison = ""
            if isinstance(result, dict):
                if "comparison" in result:
                    comparison = result["comparison"]
                elif "summary" in result:
                    comparison = result["summary"]
                elif "content" in result:
                    comparison = result["content"]
            elif isinstance(result, str):
                comparison = result
            
            # Update state
            for url in urls:
                if url not in self._pages_visited:
                    self._pages_visited.append(url)
            
            return self._create_research_result(True, comparison)
        except Exception as e:
            return self._create_research_result(False, error_message=str(e))
    
    def find_primary_sources(self, topic: str) -> ResearchResult:
        """
        Find primary sources on a specific topic.
        
        Args:
            topic: The topic to find primary sources for
        """
        try:
            # Create a primary sources task
            task = (
                f"Find primary sources on the topic of '{topic}' by:\n"
                f"1. Searching for academic papers, official reports, and original documents\n"
                f"2. Identifying authoritative sources like government websites, educational institutions, and recognized experts\n"
                f"3. Evaluating the credibility and reliability of each source\n"
                f"4. Extracting key information from each primary source\n"
                f"5. Organizing the sources by type, relevance, and authority\n"
                f"6. Providing a summary of the most valuable primary sources found"
            )
            
            # Set up the browser agent and execute the task
            asyncio.run(self._setup_browser_agent(task))
            result = asyncio.run(self._browser_agent.run())
            
            # Process the result
            sources_info = ""
            if isinstance(result, dict):
                if "primary_sources" in result:
                    sources_info = result["primary_sources"]
                elif "sources" in result:
                    sources_info = result["sources"]
                elif "summary" in result:
                    sources_info = result["summary"]
            elif isinstance(result, str):
                sources_info = result
            
            return self._create_research_result(True, sources_info)
        except Exception as e:
            return self._create_research_result(False, error_message=str(e))
    
    def track_topic_over_time(self, topic: str, time_period: str) -> ResearchResult:
        """
        Track how a topic has evolved over a specific time period.
        
        Args:
            topic: The topic to track
            time_period: The time period to track (e.g., "last 5 years", "2010-2020")
        """
        try:
            # Create a topic tracking task
            task = (
                f"Track how the topic of '{topic}' has evolved over {time_period} by:\n"
                f"1. Searching for information from different points in time\n"
                f"2. Identifying key developments, changes in understanding, or shifts in perspective\n"
                f"3. Noting important events, publications, or discoveries that influenced the topic\n"
                f"4. Creating a timeline of significant developments\n"
                f"5. Analyzing trends and patterns in how the topic has been discussed\n"
                f"6. Summarizing how understanding or treatment of the topic has changed over time"
            )
            
            # Set up the browser agent and execute the task
            asyncio.run(self._setup_browser_agent(task))
            result = asyncio.run(self._browser_agent.run())
            
            # Process the result
            timeline_info = ""
            if isinstance(result, dict):
                if "timeline" in result:
                    timeline_info = result["timeline"]
                elif "evolution" in result:
                    timeline_info = result["evolution"]
                elif "summary" in result:
                    timeline_info = result["summary"]
            elif isinstance(result, str):
                timeline_info = result
            
            return self._create_research_result(True, timeline_info)
        except Exception as e:
            return self._create_research_result(False, error_message=str(e))
    
    def extract_structured_data(self, url: str, data_type: str) -> ResearchResult:
        """
        Extract structured data of a specific type from a webpage.
        
        Args:
            url: The URL to extract data from
            data_type: The type of data to extract (e.g., "table", "list", "contact information")
        """
        try:
            # Navigate to the URL first if not already on that page
            if not self._current_page or self._current_page["url"] != url:
                navigation_result = self.navigate(url)
                if not navigation_result["success"]:
                    return navigation_result
            
            # Create a data extraction task
            task = (
                f"Extract {data_type} from the current page by:\n"
                f"1. Identifying all instances of {data_type} on the page\n"
                f"2. Extracting the data in a structured format\n"
                f"3. Organizing the data in a clear and usable way\n"
                f"4. Providing context for the extracted data\n"
                f"5. Converting the data to a format that can be easily processed (e.g., JSON, CSV)"
            )
            
            # Set up the browser agent and execute the task
            asyncio.run(self._setup_browser_agent(task))
            result = asyncio.run(self._browser_agent.run())
            
            # Process the result
            structured_data = ""
            if isinstance(result, dict):
                if "structured_data" in result:
                    structured_data = result["structured_data"]
                elif "data" in result:
                    structured_data = result["data"]
                elif "content" in result:
                    structured_data = result["content"]
            elif isinstance(result, str):
                structured_data = result
            
            return self._create_research_result(True, structured_data)
        except Exception as e:
            return self._create_research_result(False, error_message=str(e))
    
    def clear_cache(self):
        """Clear the research cache."""
        self._research_cache = {}
        
        # Also clear disk cache
        if os.path.exists(self._cache_dir):
            for file in os.listdir(self._cache_dir):
                if file.endswith(".json"):
                    try:
                        os.remove(os.path.join(self._cache_dir, file))
                    except Exception:
                        # Silently fail if deletion fails
                        pass
