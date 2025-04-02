"""Main controller for the CodeAct agent framework."""


from dataclasses import dataclass

from codeact.interfaces.agent import AgentHistoryEntry, IAgentState
from codeact.interfaces.execution import ExecutionResult, IExecutionEnvironment
from codeact.interfaces.llm import ILLMOutputParser, ILLMProvider


@dataclass
class AgentConfig:
    """Configuration for the CodeAct agent."""

    max_turns: int = 5


@dataclass
class AgentDependencies:
    """Dependencies for the CodeAct agent."""

    llm_provider: ILLMProvider
    exec_env: IExecutionEnvironment
    parser: ILLMOutputParser
    agent_state: IAgentState


class CodeActAgentController:
    """Main controller for the CodeAct agent."""

    def __init__(self, deps: AgentDependencies, config: AgentConfig | None = None) -> None:
        """Initialize the agent controller with its dependencies."""
        self._llm = deps.llm_provider
        self._exec_env = deps.exec_env
        self._parser = deps.parser
        self._state = deps.agent_state
        self._config = config or AgentConfig()
        self._max_turns = self._config.max_turns
        print("CodeAct Agent Controller Initialized")
        print(f"Max Turns: {self._max_turns}")

    def _create_observation_string(self, exec_result: ExecutionResult) -> str:
        """Creates an observation string from execution results."""
        obs = "Observation: "
        if exec_result["success"]:
            obs += "Code executed successfully.\n"
        else:
            obs += "Code execution failed.\n"
        if exec_result["stdout"]:
            obs += f"STDOUT:\n{exec_result['stdout']}\n"
        if exec_result["stderr"]:
            obs += f"STDERR:\n{exec_result['stderr']}\n"
        return obs.strip()

    def run_interaction(self, initial_instruction: str) -> tuple[str, list[AgentHistoryEntry]]:
        """Runs the main interaction loop."""
        print("\n======= Starting Interaction =======")
        print(f"Initial Instruction: {initial_instruction}")
        self._state.clear_history()  # Start fresh
        self._state.add_entry("user", initial_instruction)
        observation = f"Received initial instruction: {initial_instruction}"
        final_outcome = "Agent stopped: Reason unknown."

        for turn in range(1, self._max_turns + 1):
            print(f"\n------- Turn {turn}/{self._max_turns} -------")
            current_history = self._state.get_history()

            # 1. Generate LLM Response
            raw_llm_response = self._llm.generate(prompt=observation, history=current_history)
            self._state.add_entry("assistant_raw", raw_llm_response)

            # 2. Parse LLM Response
            parsed_output = self._parser.parse(raw_llm_response)

            if parsed_output["thought"]:
                print(f"Agent Thought: {parsed_output['thought']}")
                self._state.add_entry("assistant_thought", parsed_output["thought"])

            # 3. Process Action or Solution
            if parsed_output["code_action"]:
                print("Agent Action: Execute Code")
                self._state.add_entry("assistant_action", parsed_output["code_action"])
                # Execute Code
                exec_result = self._exec_env.execute_code(parsed_output["code_action"])
                # Create next observation
                observation = self._create_observation_string(exec_result)
                self._state.add_entry("environment", observation)

            elif parsed_output["solution"]:
                print(f"Agent Solution Found: {parsed_output['solution']}")
                self._state.add_entry("assistant_solution", parsed_output["solution"])
                final_outcome = f"Task Finished. Final Answer: {parsed_output['solution']}"
                print("------- Interaction Ended (Solution) -------")
                return final_outcome, self._state.get_history()
            else:
                # Handle cases where LLM gives neither code nor solution
                # (e.g., only thought, or parse error)
                print("Agent Warning: LLM did not provide a code action or a solution this turn.")
                observation = "Observation: No specific action taken. Please proceed."
                # Add a system/agent note to history if needed
                self._state.add_entry(
                    "system_note", "LLM provided no executable action or final solution."
                )

        # Loop finished without a solution
        final_outcome = "Agent stopped: Max turns reached."
        print("------- Interaction Ended (Max Turns) -------")
        return final_outcome, self._state.get_history()
