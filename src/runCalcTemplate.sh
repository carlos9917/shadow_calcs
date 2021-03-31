#!/bin/bash
######################################################
# Template script to run the calcShadows script
# This script is called by runGrassBatchMode.sh
######################################################

source ./env.sh

now=`date '+%Y%m%d_%H%M%S'`
st=REPLACE #CHANGED by runGrassBatchMode.sh
tilesDir=stations_$st
srcdir=$GITREPO #/scripts
echo "--------------------------------"
echo "REMEMBER TO LOAD GRASS FIRST!!!"
echo "--------------------------------"

echo "Running calcShadows"
time $PYBIN ./calculateShadows.py -sl CSVFILE -si $st -td $PWD -sd $srcdir >& out_${st}_$now
echo "calcShadows done"
cd -
