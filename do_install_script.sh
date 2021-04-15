#!/bin/bash
#
# Install scripts in local directory
# Assumes git repo cloned to REPO path below.Otherwise fail
# 
# If argument provided, use repository in speficied location
# For example, in volta the $HOME directory is very small
# Could use $HOST to decide, but tried in volta and does not print anything...

REPO=$HOME/shadow_calcs

if [ ! -d $REPO ]; then  
echo "Directory $REPO does not exist!" 
echo "Either specify a path for the repository as argument or clone it on this location"
exit 1
fi

if [ -z $1 ]; then
  echo "Using $REPO repository"
else
  echo "Using user-specified path for repository: $REPO"
  REPO=$1
fi

#Do all local operations here:
LOCALDIR=$REPO/local_processing
echo Copying all necessary scripts to $LOCALDIR
mkdir $LOCALDIR
cp $REPO/operational_scripts/* $LOCALDIR
cp $REPO/data_website/* $LOCALDIR
cp $REPO/dbase_utils/*.py $LOCALDIR

cat > $LOCALDIR/env.sh << EOF
#Default set of stations for testing
CSVTEST=./station_data_test_utm.csv

#Location of git repo or wherever I copied the scripts
GITREPO=$REPO

#Location of the master scripts
SCRDIR=$REPO/src

#Local path for zip files, if they are available
DSMPATH=/data/users/cap/DSM_DK/

# -----------------------------
# Needed by runGrass.sh
# -----------------------------
#This directory is where Grass will process the data. It will be created by grass
GRASSPROJECT=$LOCALDIR/grassdata/mytemploc_dk

GRASSPROJECTSETTINGS=$REPO/config_files/RoadStations

#The grass binary
GRASSBINARY=/usr/bin/grass78
#The python binary
PYBIN=/data/users/cap/miniconda3/envs/py38/bin/python

EOF
cd $LOCALDIR
chmod 755 ./daily_processing.sh
alias d_p="$LOCALDIR/daily_processing.sh"

#Checking if hard-coded paths for DSM data, GRASS and Python are found
[ ! -f $PYBIN ] && echo "python3 binary $PYBIN not found!"; exit 1
[ ! -f $GRASSBINARY ] && echo "GRASS binary $GRASSBINARY not found!"; exit 1
[ ! -d $DSMPATH ] && echo "DSM path $DSMPATH not found!"; exit 1

