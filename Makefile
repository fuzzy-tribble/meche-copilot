######################
# Makefile for linting, testing, and formatting

# Usage:
# make help
# make lint
# make format
# etc
######################

.PHONY: all lint test

# Default target executed when no arguments are given to make.
all: help

######################
# EVALS
######################

# NOTE: prefer doing in vscode...?
# eval: 
# 	poetry run jupyter notebook --allow-root

######################
# TESTING AND COVERAGE
######################

# test:
# 	poetry run pytest

######################
# DOCUMENTATION
######################

# TODO

######################
# LINTING AND FORMATTING
######################

# Define a variable for Python and notebook files.
PYTHON_FILES=.
lint format: PYTHON_FILES=.
lint_diff format_diff: PYTHON_FILES=$(shell git diff --relative=libs/langchain --name-only --diff-filter=d master | grep -E '\.py$$|\.ipynb$$')

lint lint_diff:
	poetry run mypy $(PYTHON_FILES)
	poetry run black $(PYTHON_FILES) --check
	poetry run ruff .

format format_diff:
	poetry run black $(PYTHON_FILES)
	poetry run ruff --select I --fix $(PYTHON_FILES)

######################
# HELP
######################

help:
	@echo '===================='
	@echo '-- LINTING --'
	@echo 'format                       - run code formatters'
	@echo 'lint                         - run linters'
	@echo 'spell_check               	- run codespell on the project'
	@echo 'spell_fix               		- run codespell on the project and fix the errors'
	@echo '-- TESTS --'
	@echo 'test                         - run unit tests'
	@echo '-- EVALS --'
	@echo 'eval                         - run evals in jupyter nbs'
