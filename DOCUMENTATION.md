# CodeAct Browser-Use Integration Documentation

## Overview

This documentation covers the enhanced integration between CodeAct and browser-use, enabling AI agents to perform sophisticated web-based research tasks. The integration follows the SOLID principles of the original CodeAct framework while adding powerful new capabilities for web navigation, information extraction, and research.

## Table of Contents

1. [Architecture](#architecture)
2. [Components](#components)
3. [Installation](#installation)
4. [Basic Usage](#basic-usage)
5. [Advanced Features](#advanced-features)
6. [Error Handling](#error-handling)
7. [LLM Integration](#llm-integration)
8. [Examples](#examples)
9. [API Reference](#api-reference)

## Architecture

The integration follows an "Extended Approach" that maintains a clean separation of concerns:

1. **Research Interface**: A dedicated `IResearchEnvironment` interface defines methods for web research
2. **Browser-Use Implementation**: Multiple implementations of the research interface using the browser-use library
3. **Extended Parser**: A `ResearchAwareOutputParser` recognizes research-specific instructions
4. **Enhanced Agent Controller**: A `ResearchEnabledAgentController` handles research actions alongside code execution
5. **Error Handling**: Robust error handling mechanisms with retry logic and recovery capabilities
6. **LLM Adapters**: Adapters for connecting various LLM providers to the system

## Components

### Core Components

- **IResearchEnvironment**: Interface defining research capabilities
- **RealBrowserUseResearchEnvironment**: Basic implementation using browser-use
- **EnhancedBrowserUseResearchEnvironment**: Advanced implementation with additional features
- **ErrorHandlingResearchEnvironment**: Implementation with robust error handling
- **ResearchAwareOutputParser**: Parser that recognizes research-specific instructions
- **ResearchEnabledAgentController**: Agent controller that handles research actions
- **LLMProviderAdapter**: Adapter for connecting CodeAct's LLM providers to browser-use

### LLM Providers

- **OpenAILLMProvider**: Implementation using OpenAI's API
- **AnthropicLLMProvider**: Implementation using Anthropic's API

## Installation

### Prerequisites

- Python 3.11 or higher
- CodeAct repository
- browser-use library

### Setup

```bash
# Clone the repositories
git clone https://github.com/albeorla/codeact.git
git clone https://github.com/browser-use/browser-use.git

# Install dependencies
cd codeact
pip install -e .
pip install playwright
playwright install chromium

# Install browser-use
cd ../browser-use
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env to add your API keys
```

## Basic Usage

### Simple Research Example

```python
from codeact.interfaces.agent import SimpleAgentState
from codeact.implementations.execution import MockExecutionEnvironment
from codeact.implementations.llm import MockLLMProvider
from codeact.implementations.parser_extended import ResearchAwareOutputParser
from codeact.implementations.research_real import RealBrowserUseResearchEnvironment
from codeact.main_extended import ResearchEnabledAgentController, ExtendedAgentDependencies, ExtendedAgentConfig

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
result, history = agent.run_interaction(instruction)
print(result)
```

### LLM Instructions

The LLM can use the following tags to trigger research actions:

- `<research>...</research>`: Execute a multi-step research plan
- `<search>...</search>`: Perform a web search
- `<navigate>...</navigate>`: Navigate to a specific URL

Example LLM output:

```
<thought>
I need to research the latest advancements in quantum computing.
</thought>
<search>latest quantum computing breakthroughs 2025</search>
```

## Advanced Features

### Enhanced Research Capabilities

The `EnhancedBrowserUseResearchEnvironment` provides advanced research capabilities:

1. **Caching**: Results are cached to improve performance and reduce API calls
2. **Source Comparison**: Compare information across multiple sources
3. **Primary Source Finding**: Identify authoritative primary sources on a topic
4. **Topic Tracking**: Track how a topic has evolved over time
5. **Structured Data Extraction**: Extract and process structured data from web pages

Example usage:

```python
from codeact.implementations.research_enhanced import EnhancedBrowserUseResearchEnvironment

# Create enhanced research environment
research_env = EnhancedBrowserUseResearchEnvironment(llm_provider)

# Compare sources
result = research_env.compare_sources(
    urls=["https://source1.com", "https://source2.com"],
    topic="quantum computing"
)

# Find primary sources
result = research_env.find_primary_sources(topic="artificial intelligence")

# Track topic over time
result = research_env.track_topic_over_time(
    topic="quantum computing",
    time_period="last 5 years"
)

# Extract structured data
result = research_env.extract_structured_data(
    url="https://example.com/data",
    data_type="table"
)
```

## Error Handling

The `ErrorHandlingResearchEnvironment` provides robust error handling with:

1. **Automatic Retries**: Failed operations are automatically retried
2. **Error Logging**: Detailed error logs for debugging
3. **Graceful Degradation**: Fallback results when operations fail
4. **Browser Recovery**: Mechanisms to recover from browser crashes
5. **Timeout Handling**: Proper handling of operations that take too long

Example usage:

```python
from codeact.implementations.error_handling import ErrorHandlingResearchEnvironment

# Create research environment with error handling
research_env = ErrorHandlingResearchEnvironment(
    llm_provider=llm_provider,
    max_retries=3,
    retry_delay=2
)

# Operations will automatically retry on failure
result = research_env.navigate("https://example.com")

# Get error log for analysis
error_log = research_env.get_error_log()
```

## LLM Integration

The integration supports multiple LLM providers:

### OpenAI

```python
from codeact.implementations.llm_providers import OpenAILLMProvider

# Create OpenAI provider
llm_provider = OpenAILLMProvider(
    model_name="gpt-4o",
    temperature=0.0,
    api_key="your-api-key"  # Optional, defaults to OPENAI_API_KEY env var
)
```

### Anthropic

```python
from codeact.implementations.llm_providers import AnthropicLLMProvider

# Create Anthropic provider
llm_provider = AnthropicLLMProvider(
    model_name="claude-3-opus-20240229",
    temperature=0.0,
    api_key="your-api-key"  # Optional, defaults to ANTHROPIC_API_KEY env var
)
```

## Examples

The integration includes several example scripts:

1. **basic_research.py**: Simple research example
2. **advanced_research.py**: Advanced research capabilities
3. **error_handling_example.py**: Error handling demonstration
4. **real_llm_test.py**: Testing with real LLM providers

Run the examples:

```bash
cd codeact-browser-use
python examples/basic_research.py
python examples/advanced_research.py
python examples/error_handling_example.py
python examples/real_llm_test.py
```

## API Reference

### IResearchEnvironment

```python
class IResearchEnvironment(Protocol):
    """Interface for research environment implementations."""
    
    def navigate(self, url: str) -> ResearchResult:
        """Navigate to a specific URL."""
        ...
    
    def search(self, query: str) -> ResearchResult:
        """Perform a web search with the given query."""
        ...
    
    def extract_info(self, selector: str) -> ResearchResult:
        """Extract specific information from the current page."""
        ...
    
    def follow_link(self, link_text: str) -> ResearchResult:
        """Follow a link on the current page."""
        ...
    
    def execute_research_plan(self, plan: str) -> ResearchResult:
        """Execute a multi-step research plan described in natural language."""
        ...
```

### EnhancedBrowserUseResearchEnvironment

Additional methods:

```python
def compare_sources(self, urls: List[str], topic: str) -> ResearchResult:
    """Compare information across multiple sources on a specific topic."""
    ...

def find_primary_sources(self, topic: str) -> ResearchResult:
    """Find primary sources on a specific topic."""
    ...

def track_topic_over_time(self, topic: str, time_period: str) -> ResearchResult:
    """Track how a topic has evolved over a specific time period."""
    ...

def extract_structured_data(self, url: str, data_type: str) -> ResearchResult:
    """Extract structured data of a specific type from a webpage."""
    ...

def clear_cache(self):
    """Clear the research cache."""
    ...
```

### ErrorHandlingResearchEnvironment

Additional methods:

```python
def get_error_log(self) -> List[Dict[str, Any]]:
    """Get the error log for analysis."""
    ...

def clear_error_log(self):
    """Clear the error log."""
    ...
```

## License

Same as the original CodeAct repository.
