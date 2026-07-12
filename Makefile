# Makefile

PYTHON ?= /usr/bin/python3
PYTHON_ID := $(shell $(PYTHON) -c 'import sys, platform; print(sys.executable, platform.python_version())' 2>/dev/null)

.DELETE_ON_ERROR:
.PHONY: all clean lint pre-commit python venv FORCE

all: venv python pre-commit

clean:
	$(RM) -r venv .python-id

lint: venv/.installed
	venv/bin/pre-commit run --all-files

pre-commit: python
	venv/bin/pre-commit install

python: venv/.installed

venv: venv/bin/pip

.python-id: FORCE
	@printf '%s\n' '$(PYTHON_ID)' | cmp -s - $@ || printf '%s\n' '$(PYTHON_ID)' > $@

venv/bin/pip: .python-id
	$(PYTHON) -m venv --clear venv

venv/.installed: requirements.txt .python-id | venv/bin/pip
	venv/bin/python3 -m pip install --upgrade pip
	venv/bin/pip install -r requirements.txt
	touch venv/.installed
