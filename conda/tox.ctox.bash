#!/bin/bash
#set -e
set -x  
for env in py35 py34 py33 p27
do 
    if [[ -z `conda env list|awk '{print $1}'|grep $env` ]]
    then   
       conda env create  -f ./conda/conda-${env}.yml
    else
       echo "environment $env already exist. Reusing ... "
    fi
    source activate $env
    pip install -r requirements.txt 
    # ctox -v -e $env  
    source deactivate
done
    

