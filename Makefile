# Makefile

.PHONY: all clean lint pre-commit python venv

all: venv python pre-commit

clean:
	$(RM) -r venv

lint: venv/bin/pre-commit
	venv/bin/pre-commit run --all-files

pre-commit: python
	venv/bin/pre-commit install

python: venv/bin/pre-commit

venv: venv/bin/pip

venv/bin/pip:
	python3 -m venv venv

venv/bin/pre-commit: requirements.txt | venv/bin/pip
	venv/bin/python3 -m pip install --upgrade pip
	venv/bin/pip install -r requirements.txt
	touch venv/bin/pre-commit
