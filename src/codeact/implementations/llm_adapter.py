"""Example adapter for connecting LLM providers to browser-use."""

from typing import Any, Dict, List, Optional, Union
from langchain.schema import HumanMessage, AIMessage, SystemMessage

class LLMProviderAdapter:
    """Adapter to connect CodeAct's ILLMProvider to browser-use's expected LLM interface."""
    
    def __init__(self, llm_provider):
        """Initialize with a CodeAct LLM provider."""
        self._llm_provider = llm_provider
        
    def __call__(
        self,
        messages: List[Dict[str, Any]],
        *,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Call the LLM with the given messages.
        
        This method adapts the browser-use expected interface to CodeAct's ILLMProvider.
        """
        # Convert browser-use message format to a format suitable for CodeAct's LLM provider
        prompt = self._format_messages_for_codeact(messages)
        
        # Generate response using CodeAct's LLM provider
        response = self._llm_provider.generate(prompt=prompt, history=[])
        
        # Return in the format expected by browser-use
        return {"content": response}
    
    def _format_messages_for_codeact(self, messages: List[Dict[str, Any]]) -> str:
        """Format browser-use messages for CodeAct's LLM provider."""
        formatted_prompt = ""
        
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if role == "system":
                formatted_prompt += f"System: {content}\n\n"
            elif role == "user":
                formatted_prompt += f"User: {content}\n\n"
            elif role == "assistant":
                formatted_prompt += f"Assistant: {content}\n\n"
            else:
                formatted_prompt += f"{content}\n\n"
                
        return formatted_prompt.strip()
