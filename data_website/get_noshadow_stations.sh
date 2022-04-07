#!/bin/bash
# Get only stations with no shadows
# 
# Set all paths and location of git repo
source ./env.sh
SERVER="gimli:8081"
SERVER="vejvejr.dk"
today=`date +'%Y%m%d'`
if [ -z $1 ]; then
  CSV=station_noshadow_$today.csv
    echo "Using server $SERVER to download only stations without shadows"
    wget -O out.tmp --user=vejvejr --password=settings "http://${SERVER}/glatinfoservice/GlatInfoServlet?command=stationlist&formatter=glatmodel&noshadow=true"
    wgetreturn=$?
    ##check if this failed:
    if [[ $wgetreturn -ne 0 ]]; then
            echo  ">>>>>>>> wget failed!!! <<<<<<<<"
            exit 1
    else
        echo "wget worked!"	    
    fi
    #Get rid of those annoying danish characters...
    #Also clean the data from columns I do not need, since this command only outputs stations missing shadow data
    #cat out.tmp | iconv -f iso8859-1 -t utf-8 | awk -F "," '{print $1 "," $2 "," $6 "," $7}'  > $CSV
    cat out.tmp | iconv -f iso8859-1 -t utf-8  > $CSV
    rm -f out.tmp
    if [ ! -s $CSV ]; then
	echo "$CSV is empty!"     
	echo "Stopping get_noshadow_stations.sh!"
        exit 1
    fi
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
    python3 ./calcUTM.py -ifile $CSV -input_format "noshadow"
else 
    echo Using $PYBIN	 
    $PYBIN ./calcUTM.py -ifile $CSV -input_format "noshadow"
fi

