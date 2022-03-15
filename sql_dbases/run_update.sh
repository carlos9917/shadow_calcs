#!/usr/bin/env bash

# Call the script to update the data
# Load conda, or point to the correct path
if [ $HOSTNAME == "9h8lvp2.usr.local" ]; then
    eval "$(/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/sources/conda/miniconda3/bin/conda shell.bash hook)"
    conda activate py39
    PY=`which python`
else
    PY="/data/users/cap/miniconda3/envs/py38/bin/python"
fi


#Local proc
DTYPES="road_stretch","noshadows"
COORDS1="/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/station_data_20211002.csv"
COORDS2="/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/station_noshadow_20211008.csv"
COORDS=$COORDS1,$COORDS2
PATH1="/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/lh_500_0.4_11.25_00"
PATH2="/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/lh_500_0.4_11.25_noshadows_20210924"
DATAPATHS=$PATH1,$PATH2

DBASE1=./shadows_road_stretches.db
DBASE2=./noshadows_daily_updates.db
DBASES=$DBASE1,$DBASE2
#$PY update_database.py -coords $COORDS -shadows $DATAPATHS -dbases $DBASES -dbase_types $DTYPES

[ ! -f $DBASE1 ] && $PY ./create_database.py

DATAPATH=/data/users/cap/glatmodel/data_shadows/shadows_new_stations
NDIRS=`ls  /data/users/cap/glatmodel/data_shadows/shadows_new_stations/ | grep lh`
COORDIR=/data/users/cap/glatmodel/data_shadows/shadows_new_stations/coord_lists
DBASES=noshadows_daily_updates.db
DTYPES="noshadows"

echo "Doing new shadows"
for DIR in $NDIRS; do
  DATE=`echo $DIR | awk '{print substr($1,28,10)}'`
  COORD=$COORDIR/station_noshadow_${DATE}.csv
  $PY update_database.py -coords $COORD -shadows $DATAPATH/$DIR -dbases $DBASES -dbase_types $DTYPES || exit 1
done

