#!/bin/bash
set -e
if [ $# -lt 1 ]; then 
   echo "Usage: $0 <minicondaenvname>"
   exit 1
fi
source activate $1
cd ui
for item in `ls *.ui|sed 's/.ui$//g'`; do 
   echo $item
   pyuic5 $item.ui > ../src/rrpam_wds/gui/_${item}.py
done
