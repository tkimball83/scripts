# Makefile

.PHONY: all clean lint pre-commit python venv

all: venv python pre-commit

clean:
	$(RM) -r venv

lint: venv/bin/pre-commit
	venv/bin/pre-commit run --all-files

venv/bin/pre-commit: requirements.txt
	test -d venv || python3 -m venv venv
	venv/bin/pip install -r requirements.txt
	touch venv/bin/pre-commit

pre-commit: python
	venv/bin/pre-commit install

python: venv
	venv/bin/python3 -m pip install --upgrade pip
	venv/bin/pip install -r requirements.txt

venv:
	test -d venv || python3 -m venv venv
