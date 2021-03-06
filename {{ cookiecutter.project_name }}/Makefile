# General.
PYTHON_EXE = python3
SHELL = /bin/bash
TOPDIR = $(shell git rev-parse --show-toplevel)

# Docker.
DOCKER_NETWORK = {{ cookiecutter.organization|lower }}
DOCKER_ORG = {{ cookiecutter.organization|lower }}
DOCKER_SVC = django
DOCKER_IMAGE_COALA = coala/base:pre

# Docker compose run generic parameters.
DOCKER_COMPOSE_RUN_CMD = docker-compose run
DOCKER_COMPOSE_RUN_OPTS = --no-deps --rm
DOCKER_COMPOSE_RUN_SVC = {{ cookiecutter.organization|lower }}-{{ cookiecutter.project_name }}-django
DOCKER_COMPOSE_RUN_FULL = $(DOCKER_COMPOSE_RUN_CMD) $(DOCKER_COMPOSE_RUN_OPTS) $(DOCKER_COMPOSE_RUN_SVC)
DOCKER_DB_CONTAINER = {{ cookiecutter.organization|lower }}-{{ cookiecutter.project_name }}-db

# Docker compose run Django parameters.
DOCKER_COMPOSE_RUN_DJANGO_MANAGE_CMD = python manage.py
DOCKER_COMPOSE_RUN_DJANGO_FULL = $(DOCKER_COMPOSE_RUN_CMD) $(DOCKER_COMPOSE_RUN_DJANGO_OPTS) $(DOCKER_COMPOSE_RUN_SVC) $(DOCKER_COMPOSE_RUN_DJANGO_MANAGE_CMD)

default: setup

help: # Display help
	@awk -F ':|##' \
		'/^[^\t].+?:.*?##/ {\
			printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
		}' $(MAKEFILE_LIST) | sort

ci-all: ci-docs  ci-linters ci-tests ## Run all the CI targets

ci-linters: ## Run the static analyzers
	@docker pull $(DOCKER_IMAGE_COALA)
	@docker run -t -v=$$(pwd):/app --workdir=/app $(DOCKER_IMAGE_COALA) coala --ci

ci-docs: ## Ensure the documentation builds
	$(DOCKER_COMPOSE_RUN_FULL) tox -e docs

ci-tests: ## Run the unit tests
	$(DOCKER_COMPOSE_RUN_FULL) tox

clean: ## Remove unwanted files in project (!DESTRUCTIVE!)
	cd $(TOPDIR) && git clean -ffdx

clean-all: clean clean-docker ## Clean everything (!DESTRUCTIVE!)

clean-docker: ## Remove all docker artifacts for this project (!DESTRUCTIVE!)
	@docker image rm -f $(shell docker image ls --filter reference='$(REPOSITORY)' -q)

dist: wheel ## Package the application

django-dbup: # Ensure Django DB is up and runnig
	@docker-compose up -d $(DOCKER_DB_CONTAINER);
	$(DOCKER_COMPOSE_RUN_CMD) $(DOCKER_COMPOSE_RUN_DJANGO_OPTS) $(DOCKER_DB_CONTAINER) bash -c "until psql -h \"$(DOCKER_DB_CONTAINER)\" -U \"postgres\" -c '\l' >/dev/null 2>&1; do sleep 1; done"

django-migrate: django-dbup ## Run the Django migrations
	$(DOCKER_COMPOSE_RUN_DJANGO_FULL) migrate

django-make-migrations: django-dbup ## Prepare the Django migrations
	$(DOCKER_COMPOSE_RUN_DJANGO_FULL) makemigrations

django-shell: django-dbup ## Run the Django Shell
	$(DOCKER_COMPOSE_RUN_DJANGO_FULL) shell

django-superuser: django-dbup ## Create the Django super user
	$(DOCKER_COMPOSE_RUN_DJANGO_FULL) createsuperuser

docker-clean: ## Stop and remove containers, volumes, networks and images for this project (!DESTRUCTIVE!)
	@docker-compose down --rmi local -v
	@docker network prune -f

docker-network: ## Create a Loannister bridge network
	FOUND=$$(docker network ls -f name=^$(DOCKER_NETWORK)$$ -q); \
	if [ -z "$$FOUND" ]; then \
		docker network create --driver bridge $(DOCKER_NETWORK); \
	fi

docs: ## Build documentation
	$(DOCKER_COMPOSE_RUN_FULL) sphinx-build -b html -d docs/build/doctrees docs/source/ docs/build/html

format: ## Format the codebase using YAPF
	$(DOCKER_COMPOSE_RUN_FULL) yapf -r -i .

format-check: ## Check the code formatting using YAPF
	$(DOCKER_COMPOSE_RUN_FULL) exit `yapf -d -r . | wc -l | tr -s ' '

setup: docker-network ## Setup the full environment (default)
	@docker-compose build
	@docker-compose pull

venv: venv/bin/activate ## Setup local venv

venv/bin/activate: requirements.txt
	test -d venv || virtualenv -p $(PYTHON_EXE) venv
	. venv/bin/activate && pip install -U pip setuptools && pip install -e .[docs,local,testing]

wheel: ## Build a wheel package
	$(DOCKER_COMPOSE_RUN_FULL) python setup.py bdist_wheel

.PHONY: ci-all ci-docs ci-linters ci-tests clean dist django-migrate django-make-migrations django-shell django-superuser docker-clean docker-network docs format format-check setup wheel
