SHELL:=/bin/bash

FORCE:

demotree.svg: FORCE
	python -m svgling '("S", ("NP", ("D", "the"), ("N", "elephant")), ("VP", ("V", "saw"), ("NP", ("D", "the"), ("N", "rhinoceros"))))' > demotree.svg

clean:
	rm -rf dist/ build/ svgling.egg-info/ test_env/

dist: setup.py svgling/ svgling/__init__.py svgling/core.py
	python setup.py sdist bdist_wheel
	@echo -e "\\nDid you remember to increment versions, and tag?"

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
