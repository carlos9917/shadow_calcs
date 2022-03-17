#!/usr/bin/env bash
if [ $HOSTNAME == glatmodelvm1p ]; then
  eval "$(/data/users/cap/miniconda3/bin/conda shell.bash hook)"
  conda activate danrapp
fi


# Checking station
#   344000  Ærø   202202 | 54.8761 | 10.3497  |   0.88 |   0.95 |
LAT=54.8761
LON=10.3497
DATE=20220202
INI=20220220
END=20220228
for DATE in `seq -w $INI $END`;do
python read_saf_clouds.py $LAT $LON $DATE
done

