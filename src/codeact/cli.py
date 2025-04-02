"""Command-line interface for the CodeAct agent."""

import argparse
import sys

from codeact.implementations.agent import InMemoryAgentState
from codeact.implementations.execution import MockExecutionEnvironment
from codeact.implementations.llm import MockLLMProvider, RegexLLMOutputParser
from codeact.main import AgentConfig, AgentDependencies, CodeActAgentController


def main() -> int:
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description="CodeAct: An agent framework for code execution and reasoning"
    )
    parser.add_argument(
        "--instruction",
        type=str,
        default="Test the execution environment and report findings.",
        help="Initial instruction for the agent",
    )
    parser.add_argument(
        "--max-turns", type=int, default=5, help="Maximum number of turns for the agent"
    )
    args = parser.parse_args()

    # Create instances of the concrete implementations
    llm_provider_instance = MockLLMProvider()
    exec_env_instance = MockExecutionEnvironment()
    parser_instance = RegexLLMOutputParser()
    agent_state_instance = InMemoryAgentState()

    # Create agent configuration and dependencies
    agent_config = AgentConfig(max_turns=args.max_turns)
    agent_deps = AgentDependencies(
        llm_provider=llm_provider_instance,
        exec_env=exec_env_instance,
        parser=parser_instance,
        agent_state=agent_state_instance,
    )

    # Create the controller
    agent_controller = CodeActAgentController(deps=agent_deps, config=agent_config)

    # Run the interaction
    final_result, _ = agent_controller.run_interaction(initial_instruction=args.instruction)

    print(f"\n======= Final Outcome ========\n{final_result}")

    # Optional: Print final history
    # print("\n======= Full History Trace =======")
    # for i, entry in enumerate(history):
    #     print(f"{i+1}. Role: {entry['role']}")
    #     print(f"   Content: {entry['content'][:300]}...") # Truncate long content
    # print("==============================")

    return 0


if __name__ == "__main__":
    sys.exit(main())
