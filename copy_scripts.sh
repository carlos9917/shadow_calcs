#!/bin/bash

#Copy all  necessary scripts to specified location

if [ -z $1 ]; then
 echo Please provide destination
 exit 1
else
  DEST=$1
fi

cp operational_scripts/* $DEST
cp data_website/* $DEST
cp dbase_utils/* $DEST

