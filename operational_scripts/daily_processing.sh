#!/bin/bash
# Script to process new stations
# 1. Get station data from gimli
# 2. Check if the data has been processed by looking for station(s) in sqlite dbase.
# 3. If not, then process the data

# Set all paths and location of git repo
source ./env.sh

WRKDIR=$PWD
now=`date '+%Y%m%d_%H%M%S'`
today=`date '+%Y%m%d'`
cwd=$PWD

echo "--------------------------------------------"
echo "Daily station processing on $now"
echo "--------------------------------------------"


cp -r $GITREPO/config_files/RoadStations ./grassdata
cp $GITREPO/config_files/rc_files/rc* $HOME/.grass7

# Step 1.
#---------------------------------------------------------
# Run script to pullout station list from gimli server
#---------------------------------------------------------
bash ./get_data.sh

csv=station_data_${today}_utm.csv
st=00 # TODO: set this as per day

#Output directory for all the processing
OUTDIR=$WRKDIR/stations_$st

# Step 2. Copy the scripts here
cp $SCRDIR/search_zipfiles_nounzip.py .
cp $SCRDIR/grab_data_dsm.py .
cp $SCRDIR/calculateShadows.py .
cp $SCRDIR/shadowFunctions.py .
cp $SCRDIR/shadows_conf.ini .
cp $GITREPO/data_website/get_data.sh .
cp $GITREPO/data_website/calcUTM.py .


# Step 3. Get the zip files I need. 
# grab_data will check the list of stations and drop them if they have been processed
# already, according to the contents of the database. 
  $PYBIN grab_data_dsm.py -ul $WRKDIR/$csv -cid $st -out $WRKDIR -td $GITREPO -lz -dsm $DSMPATH #lz for local data
  #check length of list after cleaning:
  csv_len=`wc -l $WRKDIR/$csv | awk '{print $1}'`
  echo "Length of $WRKDIR/$csv: $csv_len"

  if [ $csv_len == 0 ]; then
    EXTDSM=0
  else
    EXTDSM=1
  fi

if [ $EXTDSM == 1 ]; then
  echo " >>>> Extracting necessary zip files"
  cd $OUTDIR
  for zip in `ls *.zip`; do
   echo "unzipping $zip"
   unzip $zip
   pid=$!
   wait $pid
   echo "deleting $zip"
   rm -f $zip
   pid=$!
   wait $pid
  done
else
  echo ">>>> Not extracting zip data"
  echo ">>>> Station data has been processed already"
  echo ">>>> Exiting..."
  exit 0
fi

# Step 4. Run GRASS
#---------------------------------------------------------
# Some dirs needed by Grass
#---------------------------------------------------------
[ ! -d ./grassdata ] && mkdir ./grassdata
[ ! -d $HOME/.grass7 ] && mkdir $HOME/.grass7
 cd $WRKDIR
 echo ">>>> Files unzip DONE. Calling Grass. Doing station list $st"
 time /bin/bash ./runGrass.sh $st $csv >& salida_${st}
 pid=$!
 wait $pid
 echo "Station list $st finished."
 echo "Removing tif files for this station list"
 #to clean the data:
 cd $WRKDIR/stations_${st}
 echo "Deleting tif files"
 #rm -f *.tif *.zip *.md5
 rm -f *.tif *.md5
 pid=$!
 wait $pid
echo "Finished"

# Step 5. Update database
#Go back to original directory

#make a copy of the database (for debugging)
# echo DEBUG operation. Keep a copy of current database before updating
# cp ./shadows_data.db dbase_backup/shadows_data_$today.db
cd $cwd
rep=""
csv_ll="${csv/_utm$rep/}"
echo ">>>> Using $csv_ll  to update database"
$PYBIN ./create_dbase.py $csv_ll ./lh_500_0.4_11.25_$st
mv ./lh_500_0.4_11.25_$st ./lh_500_0.4_11.25_${today}
