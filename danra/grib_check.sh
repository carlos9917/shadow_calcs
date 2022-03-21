#!/usr/bin/env bash

# Variables I want:
# indicatorOfParameter,levelType,level
# 34 105 50 0
VAR="34 105 50 0"
DATA=/data/projects/nckf/danra/storms/NEA/2022012900
for FILE in `ls -1 $DATA`; do
echo "$FILE"
grib_ls -p indicatorOfParameter,levelType:i,level,timeRangeIndicator,time $DATA/018 | awk '{$2=$2};1' #| grep $VAR
exit
done

