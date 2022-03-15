#!/usr/bin/env bash

# Call the script to update the data
# Load conda, or point to the correct path
if [ $HOSTNAME == "9h8lvp2.usr.local" ]; then
    eval "$(/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/sources/conda/miniconda3/bin/conda shell.bash hook)"
    conda activate py39
    PY=`which python`
else
    PY="PathToCondainVolta"
fi


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
[ ! -f $DBASE1 ] && $PY ./create_database.py

$PY update_database.py -coords $COORDS -shadows $DATAPATHS -dbases $DBASES -dbase_types $DTYPES
