#!/bin/bash
set -e

if [ ! -f setup.py ] 
then 
   echo "Run this script at the top level of the repo!"
   exit 1
fi

if [ $# -lt 1 ] 
then 
   echo "Usage : $0 <env1> <env2> ..."
   echo "Available values py27, py33, py35, py34"
   exit 1
fi

for env in "$@" 
do 
    if [[ -z `conda env list|awk '{print $1}'|grep $env` ]]
    then   
       conda create --name=${env} `head -n1 requirements_conda.txt`
    else
       echo "environment $env already exist. Reusing ... "
    fi
    source activate $env
    pip install  -r ./requirements.txt
    pip install  -r ./docs/requirements.txt
    pip install    sphinxcontrib-spelling
    pip install    pyenchant
    export SPELLCHECK=1
    sphinx-build -b spelling docs dist/docs
    python setup.py check --strict --metadata --restructuredtext
    sphinx-build -b html docs dist/docs
    sphinx-build -b linkcheck docs dist/docs


    check-manifest 
    flake8 src service/*.py tests setup.py  freeze.py
    isort --verbose --check-only --diff --recursive src tests setup.py

    python ./service/installreq.py 
    pytest  --cov --cov-report=term-missing -vv
    coverage combine --append
    coverage report
 
  
    source deactivate
done
    

