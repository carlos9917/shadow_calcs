#!/bin/bash
#Set some paths

#Default set of stations for testing
CSVTEST=./station_data_test.csv

#Location of git repo or wherever I copied the scripts
GITREPO=/media/cperalta/USB128_extra/data/shadow_calcs
GITREPO=/data/users/cap/glatmodel/shadow_calcs


#Location of the master scripts
SCRDIR=$GITREPO/src

#Local path for zip files, if they are available
DSMPATH=/media/cperalta/USB128_extra/data/dsm_example/
#DSMPATH=/media/cperalta/7E95ED15444BBB52/Backup_Work/DMI/DATA_RoadProject
DSMPATH=/data/users/cap/DSM_DK/

#This one not being used yet
EXTDSM=1 #0 for NOT extracting, 1 for extracting 

# -----------------------------
# Needed by runGrass.sh
# -----------------------------
#This directory is where Grass will process the data. It will be created by grass
GRASSPROJECT=$HOME/gis/grassdata/mytemploc_dk
GRASSPROJECT=/data/users/cap/glatmodel/tests/grassdata/mytemploc_dk

#Directory where the template for PERMANENT is stored
#GRASSPROJECTSETTINGS=$HOME/gis/grassdata #/RoadStations
GRASSPROJECTSETTINGS=$GITREPO/config_files/RoadStations

#The grass binary
#GRASSBINARY=/usr/local/bin/grass79
GRASSBINARY=/usr/bin/grass78
#GRASSBINARY=/media/cperalta/USB128_extra/data/sources/gis/grass79/bin/grass79

#The python binary
PYBIN=/data/users/cap/miniconda3/envs/py38/bin/python
