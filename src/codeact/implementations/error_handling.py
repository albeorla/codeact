"""Error handling mechanisms for the browser-use integration with CodeAct."""

import asyncio
import time
import traceback
from typing import Dict, Any, Optional, List, Callable

from codeact.interfaces.research import ResearchResult, WebPage
from codeact.implementations.research_enhanced import EnhancedBrowserUseResearchEnvironment


class ErrorHandlingResearchEnvironment(EnhancedBrowserUseResearchEnvironment):
    """Research environment with robust error handling and recovery mechanisms."""
    
    def __init__(self, llm_provider, max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize with error handling configuration.
        
        Args:
            llm_provider: The LLM provider to use
            max_retries: Maximum number of retry attempts for failed operations
            retry_delay: Delay in seconds between retry attempts
        """
        super().__init__(llm_provider)
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._error_log: List[Dict[str, Any]] = []
    
    def _log_error(self, operation: str, error: Exception, context: Dict[str, Any] = None):
        """Log an error for later analysis."""
        error_entry = {
            "timestamp": time.time(),
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }
        self._error_log.append(error_entry)
    
    def _with_retry(self, operation_name: str, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute an operation with automatic retry on failure.
        
        Args:
            operation_name: Name of the operation for logging
            operation: The function to execute
            *args, **kwargs: Arguments to pass to the operation
        
        Returns:
            The result of the operation or an error result
        """
        last_error = None
        context = {"args": args, "kwargs": kwargs}
        
        for attempt in range(1, self._max_retries + 1):
            try:
                result = operation(*args, **kwargs)
                if attempt > 1:
                    # Log successful retry
                    self._log_error(
                        f"{operation_name}_retry_success",
                        Exception(f"Succeeded on attempt {attempt}"),
                        context
                    )
                return result
            except Exception as e:
                last_error = e
                self._log_error(
                    f"{operation_name}_attempt_{attempt}",
                    e,
                    context
                )
                
                if attempt < self._max_retries:
                    # Wait before retrying
                    time.sleep(self._retry_delay)
        
        # All retries failed
        return self._create_research_result(
            False,
            error_message=f"Operation {operation_name} failed after {self._max_retries} attempts: {str(last_error)}"
        )
    
    def _create_fallback_result(self, operation: str, error: Exception) -> ResearchResult:
        """Create a fallback result when an operation fails completely."""
        error_message = f"Error in {operation}: {str(error)}"
        
        # Create a basic fallback result
        return {
            "success": False,
            "pages_visited": self._pages_visited,
            "current_page": self._current_page,
            "extracted_info": f"The {operation} operation could not be completed due to an error. Please try again or try a different approach.",
            "error_message": error_message
        }
    
    def navigate(self, url: str, use_cache: bool = True) -> ResearchResult:
        """Navigate to a URL with error handling and retries."""
        return self._with_retry(
            "navigate",
            super().navigate,
            url,
            use_cache
        )
    
    def search(self, query: str, use_cache: bool = True) -> ResearchResult:
        """Perform a search with error handling and retries."""
        return self._with_retry(
            "search",
            super().search,
            query,
            use_cache
        )
    
    def extract_info(self, selector: str, use_cache: bool = True) -> ResearchResult:
        """Extract information with error handling and retries."""
        return self._with_retry(
            "extract_info",
            super().extract_info,
            selector,
            use_cache
        )
    
    def follow_link(self, link_text: str, use_cache: bool = True) -> ResearchResult:
        """Follow a link with error handling and retries."""
        return self._with_retry(
            "follow_link",
            super().follow_link,
            link_text,
            use_cache
        )
    
    def execute_research_plan(self, plan: str, use_cache: bool = True) -> ResearchResult:
        """Execute a research plan with error handling and retries."""
        return self._with_retry(
            "execute_research_plan",
            super().execute_research_plan,
            plan,
            use_cache
        )
    
    def compare_sources(self, urls: List[str], topic: str) -> ResearchResult:
        """Compare sources with error handling and retries."""
        return self._with_retry(
            "compare_sources",
            super().compare_sources,
            urls,
            topic
        )
    
    def find_primary_sources(self, topic: str) -> ResearchResult:
        """Find primary sources with error handling and retries."""
        return self._with_retry(
            "find_primary_sources",
            super().find_primary_sources,
            topic
        )
    
    def track_topic_over_time(self, topic: str, time_period: str) -> ResearchResult:
        """Track a topic over time with error handling and retries."""
        return self._with_retry(
            "track_topic_over_time",
            super().track_topic_over_time,
            topic,
            time_period
        )
    
    def extract_structured_data(self, url: str, data_type: str) -> ResearchResult:
        """Extract structured data with error handling and retries."""
        return self._with_retry(
            "extract_structured_data",
            super().extract_structured_data,
            url,
            data_type
        )
    
    def get_error_log(self) -> List[Dict[str, Any]]:
        """Get the error log for analysis."""
        return self._error_log
    
    def clear_error_log(self):
        """Clear the error log."""
        self._error_log = []


class TimeoutHandler:
    """Utility class for handling timeouts in research operations."""
    
    @staticmethod
    async def with_timeout(coro, timeout_seconds: int, fallback_result: Any = None):
        """
        Execute a coroutine with a timeout.
        
        Args:
            coro: The coroutine to execute
            timeout_seconds: Timeout in seconds
            fallback_result: Result to return if timeout occurs
            
        Returns:
            The result of the coroutine or the fallback result if timeout occurs
        """
        try:
            return await asyncio.wait_for(coro, timeout=timeout_seconds)
        except asyncio.TimeoutError:
            return fallback_result


class BrowserRecoveryHandler:
    """Utility class for recovering from browser crashes or hangs."""
    
    @staticmethod
    async def recover_browser(browser_agent):
        """
        Attempt to recover a crashed or hanging browser.
        
        Args:
            browser_agent: The browser agent to recover
            
        Returns:
            True if recovery was successful, False otherwise
        """
        try:
            # Close the current browser if it exists
            if hasattr(browser_agent, 'browser') and browser_agent.browser:
                try:
                    await browser_agent.browser.close()
                except Exception:
                    # Ignore errors when closing an already crashed browser
                    pass
            
            # Create a new browser instance
            if hasattr(browser_agent, 'create_browser'):
                await browser_agent.create_browser()
                return True
            
            return False
        except Exception:
            return False
