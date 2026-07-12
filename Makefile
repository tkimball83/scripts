# Makefile

PYTHON ?= /usr/bin/python3

.DELETE_ON_ERROR:
.PHONY: all clean lint pre-commit python venv

all: venv python pre-commit

clean:
	$(RM) -r venv

lint: venv/.installed
	venv/bin/pre-commit run --all-files

pre-commit: python
	venv/bin/pre-commit install

python: venv/.installed

venv: venv/bin/pip

venv/bin/pip:
	$(PYTHON) -m venv venv

venv/.installed: requirements.txt | venv/bin/pip
	venv/bin/python3 -m pip install --upgrade pip
	venv/bin/pip install -r requirements.txt
	touch venv/.installed
