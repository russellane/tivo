include Python.mk
PROJECT = tivo
COV_FAIL_UNDER = 31
lint :: mypy
doc :: README.md
