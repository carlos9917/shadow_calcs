#!/usr/bin/env bash

# Check some periods in danra data

if [ $HOSTNAME == glatmodelvm1p ]; then
  eval "$(/data/users/cap/miniconda3/bin/conda shell.bash hook)"
  conda activate danrapp
fi

DATADIR=/data/projects/nckf/danra/storms/NEA

loop_locations()
{
  for i in "${!STATIONS[@]}"; do
   LAT=${LATS[i]}
   LON=${LONS[i]}
   STATION=${STATIONS[i]}
    for DTG in ${DTGS[@]}; do
       python read_nea_data.py $STATION $LAT $LON $DTG
    done
  done
}


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

#DATE=2022012812
# Periods
#python read_nea_data.py $STATION $LAT $LON $DATE

DATES=(`seq -w 20220127 20220131`) # Dates for storm Malik
DATES=(`seq -w 20220216 20220220`) # Dates for storm Nora
DTGS=()
#include the hour in the dates:
for i in "${!DATES[@]}"; do
    for DTG in `seq -w 0 6 18`; do
	DTGS+=(${DATES[i]}${DTG})
    done
done

# Loop through the stations for all dates
STATIONS=(Bellahoej Kastrup)
LATS=(55.700 55.6140)
LONS=(12.508 12.6454)
loop_locations
