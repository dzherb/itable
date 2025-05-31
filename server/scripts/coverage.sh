#!/usr/bin/env bash
uv run coverage run --source='../' manage.py test
uv run coverage html

coverage_index_path=$(cd htmlcov && pwd)/index.html
uv run -m webbrowser -t file:///$coverage_index_path
