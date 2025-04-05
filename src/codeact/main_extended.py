"""Extended agent controller with research capabilities."""

from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict, Any

from codeact.interfaces.agent import AgentHistoryEntry, IAgentState
from codeact.interfaces.execution import IExecutionEnvironment
from codeact.interfaces.llm import ILLMOutputParser, ILLMProvider
from codeact.interfaces.research import IResearchEnvironment, ResearchResult
from codeact.main import CodeActAgentController, AgentConfig, AgentDependencies


@dataclass
class ExtendedAgentConfig(AgentConfig):
    """Extended configuration for the CodeAct agent with research capabilities."""
    
    enable_research: bool = True
    research_timeout: int = 120  # Timeout for research operations in seconds
    max_pages_per_task: int = 10  # Maximum number of pages to visit per task


@dataclass
class ExtendedAgentDependencies(AgentDependencies):
    """Extended dependencies for the CodeAct agent with research capabilities."""
    
    llm_provider: ILLMProvider
    exec_env: IExecutionEnvironment
    parser: ILLMOutputParser
    agent_state: IAgentState
    research_env: IResearchEnvironment  # New dependency


class ResearchEnabledAgentController(CodeActAgentController):
    """Extended agent controller with research capabilities."""
    
    def __init__(self, deps: ExtendedAgentDependencies, config: Optional[ExtendedAgentConfig] = None) -> None:
        """Initialize with extended dependencies and config."""
        super().__init__(deps, config or ExtendedAgentConfig())
        self._research_env = deps.research_env
        self._extended_config = config or ExtendedAgentConfig()
        print("Research-Enabled Agent Controller Initialized")
        print(f"Research Enabled: {self._extended_config.enable_research}")
        print(f"Research Timeout: {self._extended_config.research_timeout}s")
        print(f"Max Pages Per Task: {self._extended_config.max_pages_per_task}")
    
    def _create_research_observation(self, research_result: ResearchResult) -> str:
        """Creates an observation string from research results."""
        obs = "Research Observation: "
        if research_result["success"]:
            obs += "Research task completed successfully.\n"
        else:
            obs += f"Research task failed: {research_result['error_message']}\n"
        
        if research_result["extracted_info"]:
            obs += f"Findings:\n{research_result['extracted_info']}\n"
        
        if research_result["current_page"]:
            obs += f"Current page: {research_result['current_page']['url']}\n"
            
        if research_result["pages_visited"]:
            obs += f"Pages visited: {', '.join(research_result['pages_visited'])}\n"
            
        return obs.strip()
    
    def run_interaction(self, initial_instruction: str) -> Tuple[str, List[AgentHistoryEntry]]:
        """Runs the main interaction loop with research capabilities."""
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
            
            # 2. Parse LLM Response with research awareness
            parsed_output = self._parser.parse(raw_llm_response)
            
            if parsed_output.get("thought"):
                print(f"Agent Thought: {parsed_output['thought']}")
                self._state.add_entry("assistant_thought", parsed_output["thought"])
            
            # 3. Process Action, Research, or Solution
            if self._extended_config.enable_research and parsed_output.get("research_plan"):
                print(f"Agent Action: Execute Research Plan")
                self._state.add_entry("assistant_research", parsed_output["research_plan"])
                research_result = self._research_env.execute_research_plan(parsed_output["research_plan"])
                observation = self._create_research_observation(research_result)
                self._state.add_entry("environment", observation)
                
            elif self._extended_config.enable_research and parsed_output.get("search_query"):
                print(f"Agent Action: Search Web")
                self._state.add_entry("assistant_search", parsed_output["search_query"])
                research_result = self._research_env.search(parsed_output["search_query"])
                observation = self._create_research_observation(research_result)
                self._state.add_entry("environment", observation)
                
            elif self._extended_config.enable_research and parsed_output.get("navigate_url"):
                print(f"Agent Action: Navigate Web")
                self._state.add_entry("assistant_navigate", parsed_output["navigate_url"])
                research_result = self._research_env.navigate(parsed_output["navigate_url"])
                observation = self._create_research_observation(research_result)
                self._state.add_entry("environment", observation)
                
            elif parsed_output.get("code_action"):
                # Original code execution logic
                print("Agent Action: Execute Code")
                self._state.add_entry("assistant_action", parsed_output["code_action"])
                exec_result = self._exec_env.execute_code(parsed_output["code_action"])
                observation = self._create_observation_string(exec_result)
                self._state.add_entry("environment", observation)
                
            elif parsed_output.get("solution"):
                # Original solution logic
                print(f"Agent Solution Found: {parsed_output['solution']}")
                self._state.add_entry("assistant_solution", parsed_output["solution"])
                final_outcome = f"Task Finished. Final Answer: {parsed_output['solution']}"
                print("------- Interaction Ended (Solution) -------")
                return final_outcome, self._state.get_history()
                
            else:
                # Handle cases where LLM gives no recognized action
                print("Agent Warning: LLM did not provide a recognized action or solution this turn.")
                observation = "Observation: No specific action taken. Please proceed."
                self._state.add_entry(
                    "system_note", "LLM provided no executable action or final solution."
                )
        
        # Loop finished without a solution
        final_outcome = "Agent stopped: Max turns reached."
        print("------- Interaction Ended (Max Turns) -------")
        return final_outcome, self._state.get_history()
