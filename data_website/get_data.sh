#!/bin/bash
# Get data from website, update database
# 
# If arg 1 not given it will generate one from server
# If arg 1 is given it will only convert lat/lon to UTM coordinates

today=`date +'%Y%m%d'`
if [ -z $1 ]; then
  CSV=station_data_$today.csv
    echo "Downloading data from vejvejr.dk"
    wget -O out.tmp --user=vejvejr --password=settings "http://vejvejr.dk/glatinfoservice/GlatInfoServlet?command=stationlist"
    #Get rid of those annoying danish characters...
    cat out.tmp | iconv -f iso8859-1 -t utf-8  > $CSV
    rm -f out.tmp
else
  CSV=$1
  echo "File provided by user: $CSV. Doing only lat/lon to UTM conversion"
fi

#echo Store station data in sqlite
#Discarding this for the moment
#python3 ./store_station_data.py station_data_${today}.csv

#convert to UTM
echo Converting coordinates to UTM
if [ -z $PYBIN ]; then
    #Should work with any version of python3, otherwise use conda
    python3 ./calcUTM.py -ifile station_data_$today.csv 
else 
    echo Using $PYBIN	 
    $PYBIN ./calcUTM.py -ifile station_data_$today.csv	
fi

