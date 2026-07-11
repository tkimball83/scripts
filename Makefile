# Makefile

.PHONY: all clean lint pre-commit python venv

all: venv python pre-commit

clean:
	$(RM) -r venv

lint: python
	venv/bin/pre-commit run --all-files

pre-commit: python
	venv/bin/pre-commit install

python: venv
	venv/bin/python3 -m pip install --upgrade pip
	venv/bin/pip install -r requirements.txt pre-commit

venv:
	test -d venv || python3 -m venv venv
