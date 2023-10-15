SHELL:=/bin/bash

testopts = "--ExecutePreprocessor.timeout=120"

.PHONY: clear clean dist test-upload check-upload upload test_env test_install render site

FORCE:

demotree.svg: FORCE
	python -m svgling '("S", ("NP", ("D", "the"), ("N", "elephant")), ("VP", ("V", "saw"), ("NP", ("D", "the"), ("N", "rhinoceros"))))' > demotree.svg

clear:
	for nb in docs/*.ipynb; do jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace "$$nb" || exit 1; done

clean: clear
	rm -rf dist/ build/ svgling.egg-info/ test_env/ docs/CHANGELOG.md docs/_site

dist: setup.py svgling/ svgling/__init__.py svgling/core.py
	python setup.py sdist bdist_wheel
	@echo -e "\\nDid you remember to increment versions, update the changelog, and tag?"

test-upload:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

check-upload:
	@echo -n "This can't be undone, are you really ready to upload? [y/N] " && read ans && [ $${ans:-N} == y ] 

upload: check-upload
	twine upload dist/*

test_env:
	python -m venv test_env
	source test_env/bin/activate && pip install --upgrade pip

test_install: test_env
	source test_env/bin/activate && pip install svgwrite && pip install --index-url https://test.pypi.org/simple/ svgling

# note: assumes `svgling` in pythonpath!
# because of some weirdness in quarto, we run pre-render.py in advance and
# ensure that the changelog gets copied
site:
	python docs/pre-render.py
	quarto render docs/ --execute
