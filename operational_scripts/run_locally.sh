#!/usr/bin/env bash

# Script to run both shadows and noshadows data from glatmodel VM
TODAY=`date '+%Y%m%d'`
#Processing both data sets for shadows
eval "$(/data/users/cap/miniconda3/bin/conda shell.bash hook)"
conda activate py38
GITREPO=/data/users/cap/glatmodel/shadow_calcs
cd $GITREPO/local_processing
echo "Doing road stations"
./daily_processing.sh >& ./out_daily_call_${TODAY}
pid=$!
wait $pid
echo "Daily processing $pid finished"
echo "Doing new shadow data"
./noshadows_proc.sh >& ./out_noshadows_call_${TODAY}

