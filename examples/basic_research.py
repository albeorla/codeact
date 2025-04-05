"""Example script demonstrating basic research capabilities with CodeAct and browser-use."""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codeact.interfaces.agent import SimpleAgentState
from codeact.implementations.execution import MockExecutionEnvironment
from codeact.implementations.llm import MockLLMProvider
from codeact.implementations.parser_extended import ResearchAwareOutputParser
from codeact.implementations.research_real import RealBrowserUseResearchEnvironment
from codeact.main_extended import ResearchEnabledAgentController, ExtendedAgentDependencies, ExtendedAgentConfig

# Load environment variables
load_dotenv()

def main():
    """Run a simple research example."""
    print("=== CodeAct Browser-Use Research Example ===")
    
    # Initialize components
    llm_provider = MockLLMProvider()
    exec_env = MockExecutionEnvironment()
    parser = ResearchAwareOutputParser()
    agent_state = SimpleAgentState()
    research_env = RealBrowserUseResearchEnvironment(llm_provider)
    
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
    
    # Run a research task
    instruction = "Research the latest advancements in quantum computing and summarize the key findings."
    print(f"\nResearch Task: {instruction}\n")
    
    result, history = agent.run_interaction(instruction)
    
    # Print the result
    print("\n=== Research Results ===")
    print(result)
    
    # Print the interaction history
    print("\n=== Interaction History ===")
    for entry in history:
        print(f"{entry['role']}: {entry['content'][:100]}...")

if __name__ == "__main__":
    main()
