.DEFAULT_GOAL := help
SHELL := bash
DUTY := $(if $(VIRTUAL_ENV),,pdm run) duty
ifeq ($(USE_MULTIRUN),)
MULTIRUN_DUTY := $(DUTY)
export PDM_MULTIRUN_VERSIONS := 
else
MULTIRUN_DUTY := $(if $(USE_MULTIRUN),pdm multirun,) duty
export PDM_MULTIRUN_VERSIONS ?= 3.9 3.10 3.11 3.12
endif
export PDM_MULTIRUN_USE_VENVS ?= $(if $(shell pdm config python.use_venv | grep True),1,0)

args = $(foreach a,$($(subst -,_,$1)_args),$(if $(value $a),$a="$($a)"))
check_quality_args = files
docs_args = host port
release_args = version
test_args = match

BASIC_DUTIES = \
	changelog \
	clean \
	coverage \
	docs \
	docs-deploy \
	format \
	release \
	vscode

QUALITY_DUTIES = \
	check \
	check-quality \
	check-docs \
	check-types \
	check-api \
	check-dependencies \
	test

.PHONY: help
help:
	@$(DUTY) --list

.PHONY: lock
lock:
	@pdm lock -G:all

.PHONY: setup
setup:
	@bash scripts/setup.sh

.PHONY: $(BASIC_DUTIES)
$(BASIC_DUTIES):
	@$(DUTY) $@ $(call args,$@)

.PHONY: $(QUALITY_DUTIES)
$(QUALITY_DUTIES):
	$(MULTIRUN_DUTY) $@ $(call args,$@)
