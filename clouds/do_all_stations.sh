#!/usr/bin/env bash
#SBATCH --job-name=clouds
#SBATCH --qos=nf
#SBATCH --error=search_clouds-%j.err
#SBATCH --output=search_clouds-%j.out
#SBATCH --mem-per-cpu=48000


if [ $HOSTNAME == glatmodelvm1p ]; then
  eval "$(/data/users/cap/miniconda3/bin/conda shell.bash hook)"
  conda activate danrapp
else
  echo "Assuming I am using atos"
  ml conda
  conda activate glat
fi


# Checking station
#   344000  Ærø   202202 | 54.8761 | 10.3497  |   0.88 |   0.95 |
LAT=54.8761
LON=10.3497
#DATE=20220201
INI=20230306
END=20230331
CSV=all_coords_road_stretches.csv
CSV=case_study.csv
CSV=vejvejr_stations_20230626.csv
DBASE=clouds_vejvejr_202303.db

cp $CSV tmp_list.csv
sed -i '1d' tmp_list.csv
rm -rf tmp_stations
mkdir tmp_stations
split -d -a 4 -l 10 tmp_list.csv tmp_stations/vej --additional-suffix ".csv"
for F in tmp_stations/vej*; do
sed -i '1s/^/stationID,stationName,lat,lon\n/' $F
for DATE in `seq -w $INI $END`;do
echo "Doing $DATE for $F"
python read_saf_clouds.py -coords $F -date $DATE -dbase $DBASE #$LAT $LON $DATE
done
done
rm tmp_list.csv
rm -rf tmp_stations
