PROJECT = tivo
include Python.mk
lint:: mypy
doc :: README.md

test :: cov_fail_under_31
cov_fail_under_31:
	python -m pytest --cov-fail-under 31 --cov=$(PROJECT) tests
