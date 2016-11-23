#!/bin/bash
set -e
for env in w2.7 w3.3 w3.4 w3.5 
do 
  source activate $env
  conda env export > conda-${env}.yml
  source deactivate
done
   
