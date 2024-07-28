.PHONY: help
help:
	@echo "Use 'make <target>' where <target> is one of"
	@echo "deps                to install dependencies for local development."
	@echo "runserver           to start the Django server."
	@echo "migrations          to make migrations."
	@echo "migrate             to run migrations into the db."
	@echo "superuser           to create a superuser."
	@echo "collectstatic       to collect static data."
	@echo "format              to format the code."
	@echo "test                to run tests."

# Install dependencies

.PHONY: deps
deps:
	pip install -r requirements/dev.txt

# Django commands
.PHONY: runserver
runserver:
	python3 manage.py runserver

.PHONY: migrations
migrations:
	python3 manage.py makemigrations

.PHONY: migrate
migrate:
	python3 manage.py migrate

.PHONY: superuser
superuser:
	python3 manage.py createsuperuser

.PHONY: collectstatic
collectstatic: deps
	python3 manage.py collectstatic --noinput

# code formatting
.PHONY: format
format:
	isort .
	black .


# testing
.PHONY: test
test:
	pytest tests/

# local
.PHONY: prepush
prepush:
	@echo "Running CI validation on local checkout before push to remote/origin..."
	@## Install `pre-commit` if not already installed by user.
	@## NB: This operation is idempotent.
	@pre-commit install
	@## Run pre-commit checks at the project-level.
	@## NB: pre-commit automatically initializes an environment if none is found.
	@pre-commit run --all-files --show-diff-on-failure
	@echo "✅ Valid - all checks passed!"
