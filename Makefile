.PHONY: main mypy

main: mypy flake8
	python3 main.py

mypy:
	mypy .

flake8:
	flake8 .
