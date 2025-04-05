"""Example script for testing the CodeAct browser-use integration with real LLMs."""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codeact.interfaces.agent import SimpleAgentState
from codeact.implementations.execution import MockExecutionEnvironment
from codeact.implementations.parser_extended import ResearchAwareOutputParser
from codeact.implementations.error_handling import ErrorHandlingResearchEnvironment
from codeact.implementations.llm_providers import OpenAILLMProvider, AnthropicLLMProvider
from codeact.main_extended import ResearchEnabledAgentController, ExtendedAgentDependencies, ExtendedAgentConfig

# Load environment variables
load_dotenv()

def run_research_task(llm_provider, task_description):
    """Run a research task with the specified LLM provider."""
    print(f"\n=== Running Research Task with {llm_provider.__class__.__name__} ===")
    print(f"Task: {task_description}")
    
    # Initialize components
    exec_env = MockExecutionEnvironment()
    parser = ResearchAwareOutputParser()
    agent_state = SimpleAgentState()
    
    # Create research environment with error handling
    research_env = ErrorHandlingResearchEnvironment(
        llm_provider=llm_provider,
        max_retries=3,
        retry_delay=2
    )
    
    # Set up dependencies
    deps = ExtendedAgentDependencies(
        llm_provider=llm_provider,
        exec_env=exec_env,
        parser=parser,
        agent_state=agent_state,
        research_env=research_env
    )
    
    # Configure the agent
    config = ExtendedAgentConfig(
        max_turns=5,
        enable_research=True,
        research_timeout=120,
        max_pages_per_task=10
    )
    
    # Create the agent controller
    agent = ResearchEnabledAgentController(deps, config)
    
    # Run the research task
    result, _ = agent.run_interaction(task_description)
    
    print("\n=== Research Results ===")
    print(result)
    
    return result

def main():
    """Test the CodeAct browser-use integration with real LLMs."""
    print("=== CodeAct Browser-Use Real LLM Integration Test ===")
    
    # Check for API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_api_key and not anthropic_api_key:
        print("Error: No API keys found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables.")
        return
    
    # Define research tasks
    research_tasks = [
        "Research the latest developments in fusion energy and summarize the key breakthroughs in the past year.",
        "Find information about the environmental impact of electric vehicles compared to traditional vehicles.",
        "Research the current state of quantum computing and identify the leading companies in this field."
    ]
    
    # Test with OpenAI if API key is available
    if openai_api_key:
        try:
            openai_provider = OpenAILLMProvider(model_name="gpt-4o", temperature=0.0)
            for task in research_tasks:
                run_research_task(openai_provider, task)
        except Exception as e:
            print(f"Error with OpenAI provider: {str(e)}")
    
    # Test with Anthropic if API key is available
    if anthropic_api_key:
        try:
            anthropic_provider = AnthropicLLMProvider(model_name="claude-3-opus-20240229", temperature=0.0)
            for task in research_tasks:
                run_research_task(anthropic_provider, task)
        except Exception as e:
            print(f"Error with Anthropic provider: {str(e)}")

if __name__ == "__main__":
    main()
