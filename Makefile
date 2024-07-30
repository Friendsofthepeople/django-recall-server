.PHONY: collectstatic deps format help migrate migrations prepush runserver \
	superuser test

.DEFAULT_GOAL := help

# == Base ======================================================================

help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of:"
	@awk -F ':.*?## ' '/^[a-zA-Z]/ && NF==2 \
		{printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}' \
		$(MAKEFILE_LIST) | sort


# == Build =====================================================================

deps: ## install requirements for local development
	pip install -r requirements/dev.txt


# == Django ====================================================================

collectstatic: deps ## collect static files into STATIC_ROOT dir
	python3 manage.py collectstatic --noinput

migrate: migrations ## apply/unapply database migrations
	python3 manage.py migrate

migrations: ## create new migrations based on model schema changes
	python3 manage.py makemigrations

runserver: ## start the Django development server
	python3 manage.py runserver

superuser: ## create a user who can login to the admin site
	python3 manage.py createsuperuser


# == Local =====================================================================

format: ## format python src with opinionated formatter `black`
	isort .
	black .

prepush: ## verify local user checkout passes essential CI checks
	@echo "Running CI validation on local checkout before push to remote/origin..."
	@## Install `pre-commit` if not already installed by user.
	@## NB: This operation is idempotent.
	@pre-commit install
	@## Run pre-commit checks at the project-level.
	@## NB: pre-commit automatically initializes an environment if none is found.
	@pre-commit run --all-files --show-diff-on-failure
	@echo "✅ Valid - all checks passed!"


# == Test ======================================================================

test: ## run all tests on python src with `pytest`
	pytest tests/
