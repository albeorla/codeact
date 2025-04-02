# CodeAct

A framework for code execution and reasoning agents following SOLID principles and design patterns.

## Features

- **SOLID Design Principles**: Interfaces and implementations follow Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion principles
- **Design Patterns**: Implements Dependency Injection, Facade, and other patterns
- **Type Safety**: Comprehensive typing with Protocol interfaces
- **Modular Architecture**: Clean separation of concerns with well-defined interfaces
- **Dependency Management**: Poetry for managing dependencies and virtual environments
- **Code Quality**:
  - Ruff for fast linting and formatting
  - MyPy for static type checking

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Poetry (dependency management)
- Make (optional, for using the Makefile)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/codeact.git
   cd codeact
   ```

2. Install dependencies:
   ```bash
   poetry install --with dev
   ```

   This will create a `.venv` directory in the project root with all dependencies installed.

3. Activate the virtual environment (optional):
   ```bash
   # If you want to activate the virtual environment directly
   poetry shell

   # Or you can run commands directly using poetry run
   poetry run python -c "import sys; print(sys.executable)"
   ```

   Note: The Makefile commands will automatically use the correct virtual environment.

## Project Structure

```
codeact/
├── src/                       # Source code
│   └── codeact/               # Main package
│       ├── __init__.py        # Package initialization
│       ├── cli.py             # Command-line interface
│       ├── main.py            # Main agent controller
│       ├── interfaces/        # Protocol interfaces
│       │   ├── __init__.py    # Interface exports
│       │   ├── agent.py       # Agent state interfaces
│       │   ├── llm.py         # LLM provider interfaces
│       │   └── execution.py   # Code execution interfaces
│       └── implementations/   # Concrete implementations
│           ├── __init__.py    # Implementation exports
│           ├── agent.py       # Agent state implementations
│           ├── llm.py         # LLM provider implementations
│           └── execution.py   # Code execution implementations
├── tests/                     # Test suite
│   └── unit/                  # Unit tests
│       ├── test_agent.py      # Tests for agent state
│       └── test_llm.py        # Tests for LLM components
├── docs/                      # Documentation
├── Makefile                   # Automation tasks
├── pyproject.toml             # Project configuration
└── README.md                  # Project README
```

## Development Workflow

This project includes a Makefile with common development tasks:

```bash
# Install dependencies
make install

# Activate the virtual environment
make shell

# Format code
make format

# Lint code
make lint

# Run type checking
make mypy

# Run tests
make test

# Run tests with coverage
make test-cov

# Run all checks (format, lint, mypy, test)
make check

# Clean build artifacts
make clean

# Clean build artifacts and remove virtual environment
make clean-venv

# Build the package
make build

# Run the CLI application
make run
```

## Architecture

The project follows SOLID principles with a clean separation of concerns:

1. **Interfaces (Protocols)**: Define contracts for components
2. **Concrete Implementations**: Implement the interfaces
3. **Agent Controller**: Orchestrates the interaction flow using dependency injection

## License

This project is licensed under the MIT License - see the LICENSE file for details.