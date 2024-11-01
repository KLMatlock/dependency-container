.DEFAULT_GOAL := help
SHELL := bash

.PHONY: setup
setup:
	uv sync --all-extras

.PHONY: test
test:
	uv run pytest

.PHONY: format
format:
	uv run ruff format
	uv run ruff check --fix

.PHONY: lint
lint:
	uv run ruff check
	uv run pyright .

.PHONY: build
build:
	uv build
