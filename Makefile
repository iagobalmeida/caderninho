.PHONY=tests

project = caderninho
envfile_path = .env

container_composer = docker compose -p $(project) --env-file $(envfile_path)

install:
	poetry install

local:
	PYTHON_PATH='src'
	poetry run uvicorn caderninho.src.app:app --reload

coverage:
	poetry run coverage run -m pytest && coverage html && coverage.svg && coverage-badge -o coverage.svg
	poetry run coverage report

tests:
	DATABASE_URL="sqlite:aiosqlite:///test.db"
	poetry run python -m pytest -v -s

spinup:
	$(container_composer) up --build --force-recreate

spindown:
	-$(container_composer) down -v

respin: spindown spinup 