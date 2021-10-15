#!/usr/bin/env make
SHELL=/bin/bash
.SHELLFLAGS = -e -c
.ONESHELL:
MAKEFLAGS += --no-print-directory

PRJ=cythonpackage
PYTHON=python3
PYTHON_SRC=$(PRJ)/__init__.py
REQUIREMENTS=
TWINE_USERNAME?=__token__
SIGN_IDENTITY?=$(USER)

## Print all majors target
help:
	@echo "$(bold)Available rules:$(normal)"
	echo
	sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=20 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')

	echo -e "Use '$(cyan)make -jn ...$(normal)' for Parallel run"
	echo -e "Use '$(cyan)make -B ...$(normal)' to force the target"
	echo -e "Use '$(cyan)make -n ...$(normal)' to simulate the build"


## Clean project
clean:
	@rm -rf .eggs $(PRJ).egg-info .mypy_cache .pytest_cache .start build nohup.out dist \
		.make-* .pytype out.json

## Test the usage of cythonpackage
test: bdist
	export PIP_EXTRA_INDEX_URL=https://pypi.org/simple
	export PIP_INDEX_URL=https://test.pypi.org/simple
	pip install --force-reinstall dist/*.whl
	read -p '...'
	cd test-cythonpackage
	rm -Rf build dist
	python setup.py bdist_wheel
	pip install --force-reinstall dist/*.whl
	cd ..
	python -c 'import foo.bar_a; foo.bar_a.print_me()'
	python -c 'import foo.bar_b; foo.bar_b.print_me()'
	python -c 'import foo.sub.sub; foo.sub.sub.print_me()'
	python -c 'import foo2.bar_c; foo2.bar_c.print_me()'
	python -c 'import foo2.bar_d; foo2.bar_d.print_me()'


# --------------------------- Distribution
dist/:
	mkdir dist

.PHONY: bdist
dist/$(subst -,_,$(PRJ_PACKAGE))-*.whl: $(REQUIREMENTS) $(PYTHON_SRC) | dist/
	@$(VALIDATE_VENV)
	export PBR_VERSION=$$(git describe --tags)
	$(PYTHON) setup.py bdist_wheel

## Create a binary wheel distribution
bdist: dist/$(subst -,_,$(PRJ_PACKAGE))-*.whl | dist/

.PHONY: sdist
dist/$(PRJ_PACKAGE)-*.tar.gz: $(REQUIREMENTS) | dist/
	@$(VALIDATE_VENV)
	$(PYTHON) setup.py sdist

sdist: dist/$(PRJ_PACKAGE)-*.tar.gz | dist/

.PHONY: clean-dist dist

clean-dist:
	rm -Rf dist/*

# see https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/
## Create a full distribution
dist: clean-dist bdist sdist
	@echo -e "$(yellow)Package for distribution created$(normal)"

.PHONY: check-twine test-keyring test-twine
## Check the distribution before publication
check-twine: bdist
	@$(VALIDATE_VENV)
	twine check \
		$(shell find dist/ -type f \( -name "*.whl" -or -name '*.gz' \) -and ! -iname "*dev*" )

## Create keyring for Test-twine
test-keyring:
	@[ -s "$$TWINE_USERNAME" ] && read -p "Test Twine username:" TWINE_USERNAME
	keyring set https://test.pypi.org/legacy/ $$TWINE_USERNAME

## Publish distribution on test.pypi.org
test-twine: dist check-twine
	@$(VALIDATE_VENV)
	[[ $$( find dist/ -name "*.dev*.whl" | wc -l ) == 0 ]] || \
		( echo -e "$(red)Add a tag version in GIT before release$(normal)" \
		; exit 1 )
	rm -f dist/*.asc
	echo -e "$(green)Enter the Pypi password$(normal)"
	twine upload --sign -i $(SIGN_IDENTITY) --repository-url https://test.pypi.org/legacy/ \
		$(shell find dist/ -type f \( -name "*.whl" -or -name '*.gz' \) -and ! -iname "*dev*" )
	echo -e "To the test repositiry"
	echo -e "$(green)export PIP_INDEX_URL=https://test.pypi.org/simple$(normal)"
	echo -e "$(green)export PIP_EXTRA_INDEX_URL=https://pypi.org/simple$(normal)"

.PHONY: keyring release

## Create keyring for release
keyring:
	@[ -s "$$TWINE_USERNAME" ] && read -p "Twine username:" TWINE_USERNAME
	keyring set https://upload.pypi.org/legacy/ $$TWINE_USERNAME

.PHONY: push-docker-release push-release release

## Publish a distribution on pypi.org
release: clean .make-validate check-twine
	@$(VALIDATE_VENV)
	[[ $$( find dist/ -name "*.dev*" | wc -l ) == 0 ]] || \
		( echo -e "$(red)Add a tag version in GIT before release$(normal)" \
		; exit 1 )
	rm -f dist/*.asc
	echo -e "$(green)Enter the Pypi password$(normal)"
	twine upload --sign \
		$(shell find dist -type f \( -name "*.whl" -or -name '*.gz' \) -and ! -iname "*dev*" )

