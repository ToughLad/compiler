# Makefile for LINE Thrift Compiler

.PHONY: help install test clean build run

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Run the compiler"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean generated files"
	@echo "  make build      - Build distribution packages"

install:
	pip install -r requirements.txt
	pip install -e .

run:
	python src/thrift_compiler.py

test:
	python -m pytest tests/

clean:
	rm -rf build/ dist/ *.egg-info
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
