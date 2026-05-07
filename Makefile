PX4_DIR := $(HOME)/PX4-Autopilot

.PHONY: sim run lint fmt typecheck test audit pre-commit all

sim:
	cd $(PX4_DIR) && PX4_SIM_HOSTNAME=$$(ip route show | grep default | awk '{print $$3}') $(MAKE) px4_sitl none_iris

run:
	venv/bin/python -m app.main

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
