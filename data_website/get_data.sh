#!/bin/bash
#Get data from website, update database
#If file name provided it will only convert dats to UTM

today=`date +'%Y%m%d'`
if [ -z $1 ]; then
  CSV=station_data_$today.csv
  echo "Downloading data from vejvejr.dk"
  #NOTE: this used to be the old server. Since 20210506 not working anymore. Refer to old email from Bjarne Laursen
  #curl http://gimli.dmi.dk:8081/glatinfoservice/GlatInfoServlet?command=stationlist | iconv -f iso8859-1 -t utf-8 > $CSV
  #wget -O out.tmp --user=vejvejr --password=settings "http://vejvejr.dk/glatinfoservice/GlatInfoServlet?command=stationlist"
   wget -O out.tmp --user=vejvejr --password=settings "http://gimli:8081/glatinfoservice/GlatInfoServlet?command=stationlist&formatter=glatmodel&noshadow=true"
  #Get rid of those annoying danish characters...
  #Also clean the data from columns I do not need, since this command only outputs stations missing shadow data
  cat out.tmp | iconv -f iso8859-1 -t utf-8 | awk -F "," '{print $1 "," $2 "," $6 "," $7}'  > $CSV
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
    python3 ./calcUTM.py station_data_$today.csv
else 
    echo Using $PYBIN	 
    $PYBIN ./calcUTM.py station_data_$today.csv	
fi

