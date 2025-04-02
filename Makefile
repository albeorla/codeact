.PHONY: install shell format lint mypy test check clean clean-venv build

install:
	poetry install --with dev

shell:
	poetry shell

format:
	poetry run ruff format .

lint:
	poetry run ruff check .

mypy:
	poetry run mypy src/codeact

test:
	poetry run pytest tests

test-cov:
	poetry run pytest --cov=codeact tests

check: format lint mypy test

clean:
	rm -rf dist
	rm -rf *.egg-info
	rm -rf **/__pycache__
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf .pytest_cache

# Use this target with caution - it will remove the virtual environment
clean-venv: clean
	rm -rf .venv

build:
	poetry build

run:
	poetry run codeact