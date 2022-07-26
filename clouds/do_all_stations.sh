#!/usr/bin/env bash
if [ $HOSTNAME == glatmodelvm1p ]; then
  eval "$(/data/users/cap/miniconda3/bin/conda shell.bash hook)"
  conda activate danrapp
fi


# Checking station
#   344000  Ærø   202202 | 54.8761 | 10.3497  |   0.88 |   0.95 |
LAT=54.8761
LON=10.3497
#DATE=20220201
INI=20220501
END=20220511
CSV=all_coords_road_stretches.csv
CSV=case_study.csv
for DATE in `seq -w $INI $END`;do
python read_saf_clouds.py -coords $CSV -date $DATE #$LAT $LON $DATE
done

