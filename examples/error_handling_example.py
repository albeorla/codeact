"""Example script demonstrating error handling in research operations."""

import asyncio
import os
import sys
import time
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codeact.interfaces.agent import SimpleAgentState
from codeact.implementations.execution import MockExecutionEnvironment
from codeact.implementations.llm import MockLLMProvider
from codeact.implementations.parser_extended import ResearchAwareOutputParser
from codeact.implementations.error_handling import ErrorHandlingResearchEnvironment
from codeact.main_extended import ResearchEnabledAgentController, ExtendedAgentDependencies, ExtendedAgentConfig

# Load environment variables
load_dotenv()

def main():
    """Run an example demonstrating error handling in research operations."""
    print("=== CodeAct Browser-Use Error Handling Example ===")
    
    # Initialize components
    llm_provider = MockLLMProvider()
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
        research_timeout=60,
        max_pages_per_task=10
    )
    
    # Create the agent controller
    agent = ResearchEnabledAgentController(deps, config)
    
    # Demonstrate error handling with potentially problematic URLs
    problematic_urls = [
        "https://example.com/nonexistent-page",
        "https://site-that-probably-doesnt-exist-123456789.com",
        "https://example.com/page-with-complex-javascript"
    ]
    
    for url in problematic_urls:
        print(f"\n=== Testing Error Handling with URL: {url} ===")
        instruction = f"Navigate to {url} and summarize the content. If there are any issues, handle them gracefully."
        print(f"Research Task: {instruction}\n")
        
        start_time = time.time()
        result, _ = agent.run_interaction(instruction)
        end_time = time.time()
        
        print(f"Result: {result}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    # Print the error log
    print("\n=== Error Log ===")
    error_log = research_env.get_error_log()
    if error_log:
        for i, error in enumerate(error_log):
            print(f"Error {i+1}:")
            print(f"  Operation: {error['operation']}")
            print(f"  Error Type: {error['error_type']}")
            print(f"  Error Message: {error['error_message']}")
            print(f"  Timestamp: {error['timestamp']}")
            print()
    else:
        print("No errors logged.")

if __name__ == "__main__":
    main()
