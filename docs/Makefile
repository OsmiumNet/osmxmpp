# Minimal Makefile for Sphinx documentation

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build
VENV          = .venv

.PHONY: html venv

# Create virtual environment and install dependencies
venv:
	python3 -m venv $(VENV)
	$(VENV)/bin/python3 -m pip install --upgrade pip
	$(VENV)/bin/python3 -m pip install -r $(SOURCEDIR)/requirements.txt --force-reinstall

# Build HTML documentation
html:
	$(VENV)/bin/$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)
