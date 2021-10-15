.PHONY: mypy flake8 all

mypy:
	mypy timber

flake8:
	flake8 timber

all: mypy flake8
