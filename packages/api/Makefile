# TruthStream backend – Makefile
# Run from packages/api

PYTHONPATH := $(shell pwd):$(PYTHONPATH)
export PYTHONPATH

.PHONY: test-unit test-integration run check install

install:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio httpx

test-unit:
	python -m pytest tests/ -v

test-integration:
	python integration_test.py

run:
	uvicorn src.main:app --host 0.0.0.0 --port 8000

check:
	@curl -sf http://127.0.0.1:8000/health || curl -sf http://127.0.0.1:8001/health || (echo "No server on 8000/8001"; exit 1)
