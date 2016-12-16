#!/bin/bash
set -e 
isort *.py  src  service/*.py -rc
autopep8 --in-place --recursive --max-line-length=100 src  service/*.py *.py  -a
autoflake --remove-all-unused-imports --remove-all-unused-imports --in-place -r src service/*.py *.py 
flake8 src *.py
isort --check-only --diff --recursive src  *.py service/*.py
check-manifest
