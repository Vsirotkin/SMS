# Makefile

.PHONY: start

start:
	uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

install:
	uv lock
	pip install -r uv.lock

test:
	pytest

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
