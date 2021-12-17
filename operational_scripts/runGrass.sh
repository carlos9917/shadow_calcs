#!/bin/bash

#########################################################
#Run GRASS in batch mode
#########################################################
#### >>>> NOTE:  Do not load python conda at this stage!!!!
source ./env.sh # This done from process_stations.sh
#Following example here:
#https://grasswiki.osgeo.org/wiki/GRASS_and_Shell#GRASS_Batch_jobs
#set -x

#This is the id and filename of the station list being processed:
if [ -z $1 ] && [ -z $2 ]; then
  echo Please provide station id and csv file
  exit 1
else
  st=$1
  csvfile=$2
fi
WRKDIR=$PWD
export grasst="$GRASSBINARY --text"

# create new temporary location for the job, exit after creation of this location
#$grasst -c $GRASSPROJECT -e
$GRASSBINARY --text -c $GRASSPROJECT -e
[ ! -d $GRASSPROJECT/PERMANENT ] && mkdir -p $GRASSPROJECT/PERMANENT
cp $GRASSPROJECTSETTINGS/PERMANENT/* $GRASSPROJECT/PERMANENT/

#Create script to run grass from template script. It will replace REPLACE in
#the template
awk -v p1=$st -v p2=$csvfile '{gsub("REPLACE",p1);gsub("CSVFILE",p2);print}'  $SCRDIR/runCalcTemplate.sh > $WRKDIR/runCalcShadows.sh

chmod 755 $WRKDIR/runCalcShadows.sh
export GRASS_BATCH_JOB="$WRKDIR/runCalcShadows.sh"
$grasst $GRASSPROJECT/PERMANENT
unset GRASS_BATCH_JOB

#cleanup
rm -rf $GRASSPROJECT
