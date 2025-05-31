#!/usr/bin/env bash
uv run ruff format
uv run ruff check --fix
uv run dotenv-linter ../.env.example ../.env