# Makefile

PYTHON ?= python3

.DELETE_ON_ERROR:
.PHONY: all check clean lint pre-commit python venv

all: pre-commit

check: python
	venv/bin/python test_tools.py

clean:
	$(RM) -r venv

lint: python
	venv/bin/pre-commit run --all-files

pre-commit: python
	venv/bin/pre-commit install

python: venv/bin/pre-commit

venv: venv/bin/pre-commit

venv/bin/pre-commit: requirements.txt
	test -x venv/bin/python || $(PYTHON) -m venv --clear venv
	venv/bin/pip install -r requirements.txt
	touch $@
