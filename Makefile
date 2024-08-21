install:
	poetry install

tests:
	flake8
	pytest -vv
	pytest --cov

build: tests
	poetry update
	poetry build

.PHONY:tests