.PHONY: install generate test run-backend run-frontend all

PYTHON ?= .venv/Scripts/python.exe

install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

generate:
	$(PYTHON) -m backend.generator.cli --scale starter --output data/starter
	$(PYTHON) -m backend.generator.cli --scale full --output data/full

test:
	$(PYTHON) -m pytest backend/tests -v

run-backend:
	$(PYTHON) -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

build-frontend:
	cd frontend && npm run build
