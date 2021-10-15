.PHONY: mypy flake8

mypy:
	mypy . --exclude old/

flake8:
	flake8 .
