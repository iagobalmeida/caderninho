.PHONY: run, server, coverage, tests, list


install:
	poetry install

server:
	PYTHON_PATH='src'
	poetry run uvicorn caderninho.src.app:app --reload

coverage:
	poetry run coverage run -m pytest && coverage html && coverage.svg && coverage-badge -o coverage.svg
	poetry run coverage report

tests:
	DATABASE_URL="sqlite:aiosqlite:///test.db"
	poetry run python -m pytest -v -s
