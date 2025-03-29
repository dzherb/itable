#!/usr/bin/env bash
ruff format
ruff check --fix
dotenv-linter ../.env.example ../.env