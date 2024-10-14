.DEFAULT_GOAL := help
SHELL := bash

.PHONY: setup
setup:
	rye sync --all-features

.PHONY: test
test:
	rye test

.PHONY: format
format:
	rye fmt

.PHONY: lint
lint:
	rye lint
	rye run pyright .
