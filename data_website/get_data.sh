#!/bin/bash
#Get data from website, update database
today=`date +'%Y%m%d'`
echo "Downloading data from gimli.dmi.dk"
curl http://gimli.dmi.dk:8081/glatinfoservice/GlatInfoServlet?command=stationlist | iconv -f iso8859-1 -t utf-8 > station_data_$today.csv

#echo Store station data in sqlite
#Discarding this for the moment
#python3 ./store_station_data.py station_data_${today}.csv

#convert to UTM
echo Converting coordinates to UTM
if [ -z $PYBIN ]; then
    #Should work with any version of python3, otherwise use conda
    python3 ./calcUTM.py station_data_$today.csv
else 
    echo Using $PYBIN	 
    $PYBIN ./calcUTM.py station_data_$today.csv	
fi

