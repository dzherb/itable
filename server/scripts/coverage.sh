#!/usr/bin/env bash
coverage run --source='../' manage.py test
coverage html

coverage_index_path=$(cd htmlcov && pwd)/index.html
python -m webbrowser -t file:///$coverage_index_path
