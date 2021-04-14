#!/bin/bash

#Copy all  necessary scripts to specified location

if [ -z $1 ] & [ -z $2 ] ; then
 echo Please provide: path to git repo and destination 
 echo ex: ../shadow_calcs  .
 exit 1
else
  GITREPO=$1
  DEST=$2
fi

cp $GITREPO/operational_scripts/* $DEST
cp $GITREPO/data_website/* $DEST
cp $GITREPO/dbase_utils/*.py $DEST

