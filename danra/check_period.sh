#!/usr/bin/env bash

# Check some periods in danra data

if [ $HOSTNAME == glatmodelvm1p ]; then
  eval "$(/data/users/cap/miniconda3/bin/conda shell.bash hook)"
  conda activate danrapp
fi

# Checking location:
#  55,700N og 12,508
# Station: Bellahøj (København)
STATION=Bellahoej
LAT=55.700
LON=12.508

#Kastrup Lufthavn (55.6140N, 12.6454E)
STATION=Kastrup
LAT=55.6140
LON=12.6454

DATE=2022012912




# Periods
python read_nea_data.py $STATION $LAT $LON $DATE

