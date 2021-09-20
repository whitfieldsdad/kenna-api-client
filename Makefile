all: clean test build

clean:
	rm -rf dist

update:
	poetry update
	poetry export -f requirements.txt -o requirements.txt --without-hashes
	poetry show --tree

test: unit-test integration-test

unit-test:
	poetry run coverage run -m pytest --ignore tests/integration --durations=0

integration-test:
	poetry run coverage run -m pytest -k tests/integration --durations=0

coverage:
	poetry run coverage html
	poetry run coverage report -m

view-coverage:
	xdg-open htmlcov/index.html

install:
	poetry install

build: test coverage
	poetry build

release: build
	poetry publish
