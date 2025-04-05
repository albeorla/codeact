"""LLM integration for testing the CodeAct browser-use research capabilities."""

import os
from typing import List, Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from codeact.interfaces.llm import ILLMProvider


class OpenAILLMProvider(ILLMProvider):
    """Implementation of ILLMProvider using OpenAI's API."""
    
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.0, api_key: Optional[str] = None):
        """
        Initialize with OpenAI configuration.
        
        Args:
            model_name: The OpenAI model to use
            temperature: Temperature parameter for generation
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key
        )
    
    def generate(self, prompt: str, history: List[Dict[str, str]] = None) -> str:
        """
        Generate a response based on the prompt and conversation history.
        
        Args:
            prompt: The prompt to generate a response for
            history: Optional conversation history
            
        Returns:
            The generated response as a string
        """
        messages = []
        
        # Convert history to messages
        if history:
            for entry in history:
                role = entry.get("role", "")
                content = entry.get("content", "")
                
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
                elif role == "system":
                    messages.append(SystemMessage(content=content))
        
        # Add the current prompt
        messages.append(HumanMessage(content=prompt))
        
        # Generate response
        response = self.client.invoke(messages)
        
        # Extract and return the content
        return response.content


class AnthropicLLMProvider(ILLMProvider):
    """Implementation of ILLMProvider using Anthropic's API."""
    
    def __init__(self, model_name: str = "claude-3-opus-20240229", temperature: float = 0.0, api_key: Optional[str] = None):
        """
        Initialize with Anthropic configuration.
        
        Args:
            model_name: The Anthropic model to use
            temperature: Temperature parameter for generation
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY environment variable)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter.")
        
        self.client = ChatAnthropic(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key
        )
    
    def generate(self, prompt: str, history: List[Dict[str, str]] = None) -> str:
        """
        Generate a response based on the prompt and conversation history.
        
        Args:
            prompt: The prompt to generate a response for
            history: Optional conversation history
            
        Returns:
            The generated response as a string
        """
        messages = []
        
        # Convert history to messages
        if history:
            for entry in history:
                role = entry.get("role", "")
                content = entry.get("content", "")
                
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
                elif role == "system":
                    messages.append(SystemMessage(content=content))
        
        # Add the current prompt
        messages.append(HumanMessage(content=prompt))
        
        # Generate response
        response = self.client.invoke(messages)
        
        # Extract and return the content
        return response.content
