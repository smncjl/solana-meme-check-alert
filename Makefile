.PHONY: install run test lint format migrate upgrade

install:
	pip install -e .[dev]

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest

lint:
	ruff check .
	mypy app

format:
	ruff check . --fix

migrate:
	alembic revision --autogenerate -m "init"

upgrade:
	alembic upgrade head
