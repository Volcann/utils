.PHONY: setup start lint help

setup:
	uv sync --all-packages

start:
	./start.sh

lint:
	uv run --package mcp-gateway ruff check mcp-gateway/src || true
	uv run --package pr-reviewer ruff check lazy-reviewer/src

help:
	@grep -E '^##' Makefile | sed 's/## //'
