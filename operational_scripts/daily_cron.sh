#!/bin/bash 
#Daily script to get stations and process them
today=`date +'%Y%m%d'`
now=`date +'%Y%m%d_%H%M%S'`
echo -----------------------------
echo Starting cron process on $now
echo -----------------------------
echo Grab data from gimli
cd $HOME/gis/process_data
./get_data.sh >& gimli_call_$today.out
pid=$!
wait $pid
echo Process stations
./process_stations.sh ./station_data_${today}_utm.csv 00 >& grass_call_${today}.out
#an email is to be sent to me whenever the process is finished
wait $pid
pid=$!
echo Send email to cap@dmi.dk
mail -s "Daily road stations processing finished"  cap@dmi.dk < grass_call_${today}.out
now=`date +'%Y%m%d_%H%M%S'`
echo ------------------------------
echo Cron process finished on $now
echo ------------------------------
