#!/bin/bash
set -e

if [ ! -f setup.py ] 
then 
   echo "Run this script at the top level of the repo!"
   exit 1
fi

python setup.py check --strict --metadata --restructuredtext
check-manifest 
flake8 src tests conda setup.py 
isort --verbose --check-only --diff --recursive src tests setup.py


for env in py35 py34 py33 p27
do 
    if [[ -z `conda env list|awk '{print $1}'|grep $env` ]]
    then   
       conda create --name=${env} `head -n1 requirements_conda.txt`
    else
       echo "environment $env already exist. Reusing ... "
    fi
    source activate $env
    python ./conda/installreq.py 
    pytest  --cov --cov-report=term-missing -vv
    coverage combine --append
    coverage report
 
  
    source deactivate
done
    

