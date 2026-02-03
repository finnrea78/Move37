.PHONY: precommit-install lint format

precommit-install:
	pre-commit install

lint:
	pre-commit run --all-files

format:
	ruff format .
	shfmt -i 4 -sr -w .
