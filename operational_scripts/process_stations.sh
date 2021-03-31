#!/bin/bash
source ./env.sh

WRKDIR=$PWD
now=`date '+%Y%m%d_%H%M%S'`
today=`date '+%Y%m%d'`
cwd=$PWD
#for i in 00; do # note: can also do 00..NN and it will add the leading 0
[ ! -d ./grassdata ] && mkdir ./grassdata
[ ! -d $HOME/.grass7 ] && mkdir $HOME/.grass7
cp -r $GITREPO/config_files/RoadStations ./grassdata
cp $GITREPO/config_files/rc_files/rc* $HOME/.grass7
if [ -z "$1" -a -z "$2" ]; then
  csv=$CSVTEST
  st=00
  echo Using standard values for csv=$csv anv st=$st
else
  csv=$1
  st=$2
  echo User provided alues for csv=$csv anv st=$st
fi
OUTDIR=$WRKDIR/stations_$st
#Copy the scripts here
cp $SCRDIR/search_zipfiles_nounzip.py .
cp $SCRDIR/grab_data_dsm.py .
cp $SCRDIR/calculateShadows.py .
cp $SCRDIR/shadowFunctions.py .
cp $SCRDIR/shadows_conf.ini .
cp $GITREPO/data_website/get_data.sh .
cp $GITREPO/data_website/calcUTM.py .


# Run script to pullout station list from gimli server
bash ./get_data.sh
exit

echo Getting zip files
if [ $EXTDSM == 1 ]; then
  $PYBIN grab_data_dsm.py -ul $WRKDIR/$csv -cid $st -out $WRKDIR -td $GITREPO -lz -dsm $DSMPATH #lz for local data
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
  echo Not extracting zip data
fi

 cd $WRKDIR
 echo "Files unzip DONE. Calling Grass. Doing station list $st"
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

#rename current data directory
cd $cwd
rep=""
csv_ll="${csv/_utm$rep/}"
echo Will use $csv_ll  to update database
$PYBIN ./create_dbase.py $csv_ll ./lh_500_0.4_11.25_00
#make a copy of the database (for debugging)
cp ./shadows_data.db dbase_backup/shadows_data_$today.db
mv ./lh_500_0.4_11.25_00 ./lh_500_0.4_11.25_00_${today}
#echo "NOTE: need to copy over my ssh key before doing this"
echo "Copying data to freyja"
#scp -r ./lh_500_0.4_11.25_00_${today} cap@freyja-2.dmi.dk:/data/cap/DSM_DK/Shadow_data/rancher_processed
