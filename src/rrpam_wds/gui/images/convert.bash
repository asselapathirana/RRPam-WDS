#!/bin/bash
set -e
if [ $# -lt 1 ];  then 
  echo "Usage: svg file name without .svg extension to create <filename>ico"
  exit 1
fi
for size in 16 32 48 128 256; do
    inkscape -z -e $size.png -w $size -h $size $1.svg >/dev/null 2>/dev/null
done
convert 16.png 32.png 48.png 128.png 256.png -colors 256 $1.ico
