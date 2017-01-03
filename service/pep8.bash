#!/bin/bash
set -e 
rootlevel='freeze.py  setupdata.py  setup.py'
isort ${rootlevel}  src  service/*.py -rc
autopep8 --in-place --recursive --max-line-length=100 src  service/*.py ${rootlevel} -a
autoflake --remove-all-unused-imports --remove-all-unused-imports --in-place -r src service/*.py ${rootlevel}
flake8 src *.py
isort --check-only --diff --recursive src  *.py service/*.py
check-manifest
