.PHONY: help install test test-all regen render notebooks privacy clean

help:
	@echo "Common targets:"
	@echo "  make install    Install the package + dev deps into the current Python env"
	@echo "  make test       Run fast pytest tests (skip slow PyMC ones)"
	@echo "  make test-all   Run all pytest tests (including slow PyMC)"
	@echo "  make regen      Regenerate every chapter's data + figures from seeds"
	@echo "  make render     Render every chapter.log to chapter.md via loglog"
	@echo "  make notebooks  Execute every chapter notebook end-to-end (in place)"
	@echo "  make privacy    Run the privacy-policy grep guard on tracked files"
	@echo "  make clean      Remove pycache, pytest cache, and ipynb checkpoints"

install:
	pip install -e ".[dev]"

test:
	pytest -m "not slow"

test-all:
	pytest

regen:
	python scripts/regenerate_all.py

render:
	python scripts/render_chapters.py

notebooks:
	@for nb in chapters/*/notebook.ipynb; do \
		echo "executing $$nb"; \
		python -c "import nbformat, sys; from nbclient import NotebookClient; nb = nbformat.read(sys.argv[1], as_version=4); NotebookClient(nb, kernel_name='expkit', timeout=600).execute(); nbformat.write(nb, sys.argv[1])" "$$nb" || exit 1; \
	done

privacy:
	bash scripts/check_privacy.sh

clean:
	find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .ipynb_checkpoints \) -prune -exec rm -rf {} +
