# コンテナ内で使うコマンド。ホストからは `make docker-test` / `make docker-chart`
.PHONY: build test chart fmt lint clean docker-test docker-chart docker-lint

build:
	cmake -S ecu -B build -DCMAKE_BUILD_TYPE=Release
	cmake --build build

test: build
	pytest

chart:
	python tools/gherkin2puml.py tests/features charts
	find charts -name '*.puml' -print0 | xargs -0 -r plantuml -tsvg -charset UTF-8
	find charts -name '*.puml' -print0 | xargs -0 -r plantuml -tpng -charset UTF-8

fmt:
	ruff check --fix .
	ruff format .
	find ecu -name '*.[ch]' -print0 | xargs -0 clang-format -i
	reformat-gherkin tests/features

lint:
	ruff check .
	ruff format --check .
	find ecu -name '*.[ch]' -print0 | xargs -0 clang-format --dry-run --Werror
	reformat-gherkin --check tests/features

clean:
	rm -rf build charts reports .pytest_cache

docker-test:
	docker compose run --rm test

docker-chart:
	docker compose run --rm dev make chart

docker-lint:
	docker compose run --rm dev make lint
