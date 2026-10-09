.PHONY: setup start lint help

setup:
	uv sync --all-packages

start:
	./start.sh

folder_setup:
	@[ -n "$(PROJECT)" ] || (echo "❌ Usage: make folder_setup PROJECT=1x2" && exit 1)
	@make -C environment folder_setup PROJECT=$(PROJECT)

curl_setup:
	@[ -n "$(PROJECT)" ] || (echo "❌ Usage: make curl_setup PROJECT=1x2" && exit 1)
	@make -C environment curl_setup PROJECT=$(PROJECT)

lint:
	uv run --package mcp-gateway ruff check mcp-gateway/src || true
	uv run --package pr-reviewer ruff check lazy-reviewer/src
	make -C workedTask lint

help:
	@grep -E '^##' Makefile | sed 's/## //'
