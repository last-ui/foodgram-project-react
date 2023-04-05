coverage:  ## Run tests with coverage
	coverage erase
	coverage run --include=dadata/* -m pytest -ra
	coverage report -m

deps:  ## Install dependencies
	pip install black coverage flake8 mypy pylint pytest tox

lint:  ## Lint and static-check
	flake8 .
	pylint .
	mypy .

push:  ## Push code with tags
	git push && git push --tags

test:  ## Run tests
	pytest -ra