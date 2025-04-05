"""Example script demonstrating advanced research capabilities with CodeAct and browser-use."""

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
from codeact.implementations.research_enhanced import EnhancedBrowserUseResearchEnvironment
from codeact.main_extended import ResearchEnabledAgentController, ExtendedAgentDependencies, ExtendedAgentConfig

# Load environment variables
load_dotenv()

def main():
    """Run an advanced research example with multiple research methods."""
    print("=== CodeAct Browser-Use Advanced Research Example ===")
    
    # Initialize components
    llm_provider = MockLLMProvider()
    exec_env = MockExecutionEnvironment()
    parser = ResearchAwareOutputParser()
    agent_state = SimpleAgentState()
    research_env = EnhancedBrowserUseResearchEnvironment(llm_provider)
    
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
        max_turns=10,
        enable_research=True,
        research_timeout=180,
        max_pages_per_task=15
    )
    
    # Create the agent controller
    agent = ResearchEnabledAgentController(deps, config)
    
    # Demonstrate multiple research capabilities
    
    # 1. Source comparison
    print("\n=== Source Comparison Example ===")
    instruction = """
    Compare the perspectives on climate change from the following sources:
    - A scientific organization
    - A government agency
    - A news outlet
    
    Identify areas of agreement and disagreement between these sources.
    """
    print(f"Research Task: {instruction}\n")
    result, _ = agent.run_interaction(instruction)
    print("Result:", result)
    
    # 2. Finding primary sources
    print("\n=== Primary Sources Example ===")
    instruction = """
    Find primary sources on the history of artificial intelligence.
    Focus on original research papers and firsthand accounts from AI pioneers.
    """
    print(f"Research Task: {instruction}\n")
    result, _ = agent.run_interaction(instruction)
    print("Result:", result)
    
    # 3. Topic tracking over time
    print("\n=== Topic Tracking Example ===")
    instruction = """
    Track how the field of quantum computing has evolved over the past decade.
    Identify key milestones, breakthroughs, and shifts in focus.
    """
    print(f"Research Task: {instruction}\n")
    result, _ = agent.run_interaction(instruction)
    print("Result:", result)
    
    # 4. Structured data extraction
    print("\n=== Structured Data Extraction Example ===")
    instruction = """
    Extract a table of data from a webpage about global economic indicators.
    Convert the data to a structured format and explain its significance.
    """
    print(f"Research Task: {instruction}\n")
    result, _ = agent.run_interaction(instruction)
    print("Result:", result)

if __name__ == "__main__":
    main()
