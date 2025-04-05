"""Extended LLM output parser with research action recognition."""

import re
from typing import Dict, Any, Optional

from codeact.interfaces.llm import ILLMOutputParser, ParsedLLMOutput
from codeact.implementations.llm import RegexLLMOutputParser


class ResearchAwareOutputParser(RegexLLMOutputParser):
    """Parser that recognizes research actions in addition to code execution."""
    
    # New patterns for research actions
    RESEARCH_RE = re.compile(r"<research>(.*?)</research>", re.DOTALL | re.IGNORECASE)
    SEARCH_RE = re.compile(r"<search>(.*?)</search>", re.DOTALL | re.IGNORECASE)
    NAVIGATE_RE = re.compile(r"<navigate>(.*?)</navigate>", re.DOTALL | re.IGNORECASE)
    
    def parse(self, llm_output: str) -> Dict[str, Any]:
        """Parses the LLM's raw string into structured components including research actions."""
        # Get base parsing from parent class
        base_parsed = super().parse(llm_output)
        
        # Add research-specific parsing
        research_match = self.RESEARCH_RE.search(llm_output)
        search_match = self.SEARCH_RE.search(llm_output)
        navigate_match = self.NAVIGATE_RE.search(llm_output)
        
        research_plan = research_match.group(1).strip() if research_match else None
        search_query = search_match.group(1).strip() if search_match else None
        navigate_url = navigate_match.group(1).strip() if navigate_match else None
        
        # Extend the parsed output
        extended_parsed = {
            **base_parsed,
            "research_plan": research_plan,
            "search_query": search_query,
            "navigate_url": navigate_url,
        }
        
        return extended_parsed
