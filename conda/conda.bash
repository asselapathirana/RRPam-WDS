#!/bin/bash
set -e
set -x
if [ $# -lt 2 ]
then 
   echo "Usage $0 <python version number> <env name>"
   echo "e.g. $0 2.7 boo or $0 3 bax"
   exit 1
fi
python=${1}
name=${2}
conda create -y -c anaconda --name $name python=$python `head -n1 requirements-conda.txt`	
source activate $name  
pip install guidata
pip install PythonQwt
pip install guiqwt
