.PHONY: lint fmt typecheck test audit pre-commit all

lint:
	ruff check src/ tests/

fmt:
	ruff format src/ tests/

typecheck:
	mypy src/

test:
	pytest

audit:
	pip-audit -r requirements.txt

pre-commit:
	pre-commit run --all-files

all: lint fmt typecheck test audit
