# CodeAct Documentation

Welcome to the CodeAct documentation. CodeAct is a framework for code execution and reasoning agents following SOLID principles and design patterns.

## Overview

CodeAct provides a modular architecture for building agents that can:
- Execute code safely
- Reason about code execution results
- Maintain conversation state
- Interact with Large Language Models (LLMs)

## Architecture

The framework follows SOLID principles with a clean separation of concerns:

1. **Interfaces (Protocols)**: Define contracts for components
2. **Concrete Implementations**: Implement the interfaces
3. **Agent Controller**: Orchestrates the interaction flow using dependency injection

## Components

### Agent State

The `IAgentState` interface defines how the agent maintains its conversation history. The `InMemoryAgentState` implementation provides a simple in-memory storage solution.

### LLM Provider

The `ILLMProvider` interface defines how the agent interacts with Large Language Models. The `MockLLMProvider` implementation provides a simple mock for testing.

### LLM Output Parser

The `ILLMOutputParser` interface defines how the agent parses the output from an LLM. The `RegexLLMOutputParser` implementation uses regular expressions to extract structured information.

### Execution Environment

The `IExecutionEnvironment` interface defines how the agent executes code. The `MockExecutionEnvironment` implementation provides a simple execution environment for testing.

## Getting Started

See the [README.md](../README.md) for installation and usage instructions.
