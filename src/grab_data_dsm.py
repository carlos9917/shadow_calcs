'''
This module extends and integrates the calcTiles.py script

'''
import subprocess
import os
import pandas as pd
from datetime import datetime
import sys
import numpy as np
from collections import OrderedDict
from search_zipfiles_nounzip import TIF_files as TIF_files
import os
import shutil

def check_transf(files):
    check_files=[]
    for f in files:
        if os.path.isfile(f):
            check_files.append(True)
        else:
            check_files.append(False)
    return all(check_files)  

def get_dsm_files(files,outdir,user="cap",password="RoadProject2020!"):
    '''
    Go through all files in list of files,
    wget each and write the output in log file.
    Check if log file contains name of the file and saved.
    Example command:
    wget --user cap --password RoadProject2020! ftp://ftp.kortforsyningen.dk/dhm_danmarks_hoejdemodel/DSM/DSM_604_68_TIF_UTM32-ETRS89.zip
    '''
    user_data={'user':user,'pass':password,
               'source':'ftp://ftp.kortforsyningen.dk/dhm_danmarks_hoejdemodel/DSM',
               'log':'log_wget.txt',
               'outdir':outdir}
    #check files is a list otherwise define as such if only one element
    if type(files) is not list:
        files=[files]
    check_transfer=[]
    for dfile in files:
        cmd='wget --user '+user_data['user']+' --password '+user_data['pass']+' -o '+user_data['log']+' '+os.path.join(user_data['source'],dfile)+' -P '+user_data['outdir']
        try:
            ret=subprocess.check_output(cmd,shell=True)
            with open(user_data['log'],"r") as f:
                log_out=f.readlines()
            #second last line of log file will contain words saved and file name if all good
            if dfile  and "saved" in log_out[-2]:
                check_transfer.append(True)
            else:
                check_transfer.append(False)
                print("File %s not transferred!"%dfile)
        except subprocess.CalledProcessError as err:
            print("Error with call %s"%cmd)
            print(err)
            check_transfer.append(False)

    #if all files were transferred, this will return True, otherwise it will be False
    return all(check_transfer)

def get_dsm_files_hpc(get_files):
    '''
    Get the files from the hpc.
    Assumes user has access throgh scp
    '''
    cmd="bash "+get_files
    try:
        ret=subprocess.check_output(cmd,shell=True)
    except subprocess.CalledProcessError as err:
        print("Error with call %s"%cmd)
        print(err)



def read_tif_list(FILE):
    tif_list=np.loadtxt(FILE,delimiter=' ',dtype=str)
    return tif_list


def calc_tiles(stretchlist):
    '''
    Split the list of stations in their corresponding tiles.
    output is an ordered dict with all the tiles needed
    (formerly the /tmp/horangle-NN/tile_Norting_Easting directory).

    Each key is of the form XXXX_YYY, where XXX is the Norting
    and YYY the Easting (both divided by 1000).
    Each key contains a list with all the stretches contained in that tile

    '''
    #Calculate number of lines in the file:
    tiles_list=OrderedDict()
    for k,stretch in stretchlist.iterrows():
        insert='|'.join([str(stretch['easting']),str(stretch['norting']),str(stretch['station']),str(stretch['sensor1']),str(stretch['sensor2'])])
        stretch_east=stretchlist['easting'][k]
        stretch_nort=stretchlist['norting'][k]
        stretch_tile = str(int(stretch_nort/1000))+'_'+str(int(stretch_east/1000))
        #print(stretch_tile)
        #define the dict comp as list if not already done
        try:
            if not isinstance(tiles_list[stretch_tile], list):
                pass
        except:
                #print("Tile %s not defined yet \n"%stretch_tile)
                tiles_list[stretch_tile] = []
        tiles_list[stretch_tile].append(insert)
    return tiles_list

def loop_tilelist(list_tiles, tif_files):
    tileside=1
    mindist=1
    maxdistance=1000
    dist=maxdistance / 1000
    tiles=OrderedDict()
    files=OrderedDict()
    for tkey in list_tiles.keys():
        tiles_list=[]
        files_list=[]
        east = int(tkey.split('_')[1])
        north = int(tkey.split('_')[0])
        #print("east and north: %d %d"%(east,north))
        tile_east = 1000 * ( east + tileside )
        tile_west = 1000 * east
        tile_north = 1000 *( north + tileside )
        tile_south = 1000 * north
        if (dist < 1 ):
            dist=mindist # was 10, then was set to 1
        domain_east = tile_west / 1000 + dist
        domain_west = tile_west / 1000 - dist
        domain_north = tile_south / 1000 + dist
        domain_south =  tile_south / 1000 - dist
        for tfile in tif_files:
            sw_corner_east = int(tfile.split('_')[3].replace('.tif',''))
            sw_corner_north = int(tfile.split('_')[2]) 
            if ( sw_corner_east <= domain_east and sw_corner_east >= domain_west and
                 sw_corner_north <= domain_north and sw_corner_north >= domain_south):
                tiles_list.append('_'.join([str(sw_corner_north), str(sw_corner_east)]))
                files_list.append(tfile)
        tiles[tkey] = tiles_list
        files[tkey] = files_list
    return tiles, files

def look_for_tiles(tiles,cdir):
    lookup_tifs=[]
    for item in tiles:
        lookup_tifs.append(''.join(['DSM_1km_',item,'.tif']))
  
    outdir=cdir
    avail_tifs=TIF_files(zipfiles=os.path.join(cdir,'zip_files_list.txt'),zipdir=os.path.join(cdir,'list_zip_contents'),outdir=outdir)
    zipfiles=avail_tifs.find_zipfiles(lookup_tifs)
    #zipfiles = locate_zipfiles(lookup_tifs,cdir,outdir)
    return zipfiles

def main(args):
    '''
    Works for any list of stations in a csv file.
    It will save results in directory stations_XX 
    '''
    utmlist=args.utm_list
    stnum=args.csv_id
    outdir=args.out_dir
    tifdir=args.tif_dir
    usehpc=args.hpc_zipfiles #true if data in hpc or in local dir
    uselocal=args.local_zipfiles #true if data in  local directory
    gen_bash_file=args.gen_bash_file
    dbase_file = args.dbase_file

    stretchlist=pd.read_csv(utmlist,sep='|',header=None)
    stretchlist.columns=['easting','norting','station','sensor1','sensor2']
    #check if the data is already in the database
    #and reduce it accordingly
    if os.path.isfile(dbase_file):
        check_stretch= check_dbase(stretchlist,utmlist,dbase_file)
        if check_stretch.empty:
            print("All data in %s already processed"%utmlist)
            print("Exiting")
            sys.exit()
    else:
        print("WARNING: No shadow database file present")
        print("A new database file will be created by calculateShadows.py")
    tif_files=read_tif_list(os.path.join(tifdir,'list_of_tif_files.txt'))
    import time
    t0 = time.time()
    #this one needs the argument 1:
    tiles_list = calc_tiles(stretchlist) #takes 11.9 sec for the whole thing
    t1 = time.time()
    total=t1-t0
    print("timing for calc_tiles %g"%total)
    t0 = time.time()
    tiles, files = loop_tilelist(tiles_list, tif_files)
    t1 = time.time()
    total=t1-t0
    print("timing for loop_tilelist %g"%total)

    #locate zip files corresponding to a particular set of tiles:
    outdir=os.path.join(outdir,'stations_'+str(stnum))
    try:
        os.mkdir(outdir)
    except:
        print("%s exists"%outdir)
    import csv
    t0 = time.time()
    zip_files=[]
    for k,tkey in enumerate(tiles.keys()):
        zip_files.extend(look_for_tiles(tiles[tkey],tifdir))
        #now write the data
        with open(os.path.join(outdir,'tilesneeded_'+str(k).zfill(3)+'.txt'), 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=" ", lineterminator=os.linesep)
            writer.writerow(tiles[tkey])

        with open(os.path.join(outdir,'filesneeded_'+str(k).zfill(3)+'.txt'), 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=" ", lineterminator=os.linesep)
            writer.writerow(files[tkey])
    uniq_zips=set(zip_files) #many will be repeated, so clean this up
    zip_files=sorted(uniq_zips)

    if gen_bash_file:
        gfile=os.path.join(outdir,'get_zipfiles_'+str(stnum)+'.sh')    
        with open(gfile,'w') as ofile:
            for zfile in zip_files:
                if usehpc:
                    hpcfile=os.path.join('/data/cap/DSM_DK/',zfile)
                    ofile.write('scp freyja-2.dmi.dk:'+hpcfile+' . \n')
                else:
                    print("printing only the zip file names")
                    ofile.write(zfile+'\n')
        t1 = time.time()
        total=t1-t0
        print("timing for the writing part: %g"%total)
    elif uselocal:
        for zfile in zip_files:
            localfile=os.path.join(args.dsm_dir,zfile)
            if os.path.isfile(localfile):
               shutil.copy2(localfile,outdir)
            else:
               print(f"{localfile} does not exist!")
    else: #default is get files from the website
        print("Transferring all files from the website")
        if not check_transf(zip_files):
            status=get_dsm_files(zip_files,outdir)
            if status:
                print("All files transferred")
            else:
                print("Some of the files were not transferred")
                print("Check error logs")
        else:
            print("Files already transferred")

def check_dbase_nodshadows(df_stretch,utmlist,dbfile):
    '''
    Eventually check the other database
    '''
    pass

def check_dbase(df_stretch,utmlist,dbfile):
    '''
    Check existing database and remove
    any existing data from df_stretch
    '''
    import sqlite3
    con=sqlite3.connect(dbfile)
    #sql_command = "SELECT * FROM station_shadows"
    #sql_command = "SELECT * FROM station_list"
    sql_command = "SELECT * FROM STATIONS"
    data_old=pd.read_sql(sql_command, con)
    df_temp=df_stretch
    repeated=[]
    for k,station in enumerate(df_stretch['station']):
        check_row=data_old[data_old['station_id']==station]
        if not check_row.empty:
            print("Dropping station %s from input list, since it is already in database"%station)
            repeated.append(str(station))
            df_temp.drop([k],inplace=True)

    con.close()
    #write the list of repeated stations
    #now=datetime.strftime(datetime.now(),'%Y%m%d_%H%M%S')
    if len(repeated) != 0:
        new_lines=[]        
        print("Re-writing the list of stations %s"%utmlist)
        back_utm=utmlist+'.save'
        print("Original list saved as %s"%back_utm)
        cmd='cp '+utmlist+' '+back_utm
        ret=subprocess.check_output(cmd,shell=True)
        with open(utmlist,'r') as f:
            utm_orig=f.readlines()
        with open(utmlist,'w') as f:
            for line in utm_orig:
                station=line.split('|')[2]
                if station not in repeated:
                    f.write(line)
    return df_temp

if __name__ == '__main__':
    import argparse
    from argparse import RawTextHelpFormatter

    parser = argparse.ArgumentParser(description='''If no argument provided it will take the default config file
             Example usage: python3 grab_data_dsm.py -ul $wrkdir/$csv -cid $st -out $wrkdir -td $scrdir''', formatter_class=RawTextHelpFormatter)

    parser.add_argument('-ul','--utm_list',
           metavar='the csv file with the stations in utm coordinates',
           type=str,
           default=None,
           required=True)
    parser.add_argument('-cid','--csv_id',
           metavar='the number of the csv file',
           type=str,
           default=None,
           required=True)

    parser.add_argument('-out','--out_dir',
           metavar='where to write the data',
           type=str,
           default=None,
           required=True)

    parser.add_argument('-td','--tif_dir',
           metavar='where to find list of tif files',
           type=str,
           default=None,
           required=True)

    parser.add_argument('-dbf','--dbase_file',
           metavar='The sqlite file with the database',
           type=str,
           default='./shadows_data.db',
           required=False)

    parser.add_argument('-hz','--hpc_zipfiles',action='store_true') # false by default
    parser.add_argument('-lz','--local_zipfiles',action='store_true') # false by default
    parser.add_argument('-bf','--gen_bash_file',action='store_true') # false by default

    #This one to be used only if setting local_zipfiles to true
    parser.add_argument('-dsm','--dsm_dir',
           metavar='local directory where DSM zip files are stored',
           type=str,
           default="/data/users/cap/DSM_DK/",
           required=False)


    args = parser.parse_args()
    main(args)

