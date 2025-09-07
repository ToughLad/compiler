# Makefile for LINE Thrift Compiler

.PHONY: help install install-dev test test-coverage test-unit test-integration clean build run lint

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make test          - Run all tests with coverage"
	@echo "  make test-coverage - Run tests and generate HTML coverage report"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make lint          - Run code quality checks"
	@echo "  make run           - Run the compiler"
	@echo "  make clean         - Clean generated files"
	@echo "  make build         - Build distribution packages"

install:
	pip install -r requirements.txt
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

test:
	python -m pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=100

test-coverage:
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

test-unit:
	python -m pytest tests/test_thrift_compiler.py -v

test-integration:
	python -m pytest tests/test_integration*.py -v

lint:
	flake8 src/ tests/ --max-line-length=120 --ignore=E203,W503
	black --check src/ tests/
	mypy src/ --ignore-missing-imports

run:
	python src/thrift_compiler.py

clean:
	rm -rf build/ dist/ *.egg-info htmlcov/ .coverage .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	python setup.py sdist bdist_wheel

output-stats:
	@echo "Checking output statistics..."
	@if [ -f ../line.thrift ]; then \
		echo "Enums:     $$(grep -c '^enum ' ../line.thrift)"; \
		echo "Structs:   $$(grep -c '^struct ' ../line.thrift)"; \
		echo "Services:  $$(grep -c '^service ' ../line.thrift)"; \
		echo "Typedefs:  $$(grep -c '^typedef ' ../line.thrift)"; \
	else \
		echo "Output file not found. Run 'make run' first."; \
	fi
