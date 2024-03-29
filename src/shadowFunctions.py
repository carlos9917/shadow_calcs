'''
Python version of the calculateShadows.sh bash script
originally used to call Grass

Nomenclature
Stretch: refers to a particular road. The original
data set was classified according to county, station number
and road section. Not sure if this naming is consistent

Routines
--------

read_stretch

read_conf


'''
import sqlite3
from datetime import datetime
import argparse
from argparse import RawTextHelpFormatter
import configparser
from collections import OrderedDict
import subprocess
import pandas as pd
import logging
import numpy as np
import os
log_file_ts = datetime.strftime(datetime.now(),"%Y%m%d_%H%M%S")
logger = logging.getLogger(__name__)

def read_stretch(stretchfile):
    '''
    Read the stretch data, with format
    easting|norting|county|station|roadsection
    stretchlist.columns=['easting','norting','id1','station','id2']

    527087.842096|6250499.367625|33|137280|131

    Parameters
    ----------
    stretchfile: `str`
                Name of the file
    Yields
    ------
    data: `DataFrame`
                A pandas dataframe with the data
    '''
    data=pd.read_csv(stretchfile,sep='|',header=None,dtype=str)
    #data.columns=['easting','norting','county','station','roadsection'] #CHANGED ON 20210924
    data.columns=['easting','norting','station','county','roadsection'] #CHANGED ON 20210924
    stretch_tile=[]
    for k,nort in enumerate(data.norting):
        east=data.easting.values[k]
        #stretch_tile.append('_'.join([str(int(nort/1000)),str(int(east/1000))]))
        stretch_tile.append('_'.join([str(int(float(nort)/1000)),str(int(float(east)/1000))]))
    #I add a new column wth the stretch file    
    data['tile'] = stretch_tile
    print("read_stretch: checking what the data is looking like here")
    print(data)
    return data

def read_conf(cfile):
    '''
    Read the config file
    '''
    conf = configparser.RawConfigParser()
    conf.optionxform = str
    logger.info("Reading config file %s"%cfile)
    conf.read(cfile)
    # read all options here:
    secs = conf.sections()
    shadowPars=OrderedDict()
    for sec in secs:
        if sec == "SHADOWS":
            options = conf.options(sec)
            for param in options:
                paramValue=conf.get(sec,param)
                shadowPars[param] = paramValue
                #print("getting this value %s for %s"%(paramValue,param))
    return shadowPars

def count_stretches():
    '''
    Calculate all tiles neeeded by a particular stretch
    '''
    pass

def call_grass(step,options,tile_data=None):
    '''
    Call grass routines
    '''
    log_file='grass_calls_'+log_file_ts+'.out'
    if step == 'set_resolution':
        logger.info("Setting resolution %s"%str(options['resolution']))
        cmd= 'echo "call set_resol\n" >> '+log_file+';g.region res='+str(options['resolution'])+' -p >> '+log_file
        try:
            out=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
        except subprocess.CalledProcessError as err:
            logger.error("Setting resolution failed with error %s"%err)
    elif step == 'set_domain':
        logger.info("Setting domain %s"%str(options['region']))
        cmd= 'echo "call set_domain\n" >> '+log_file+';g.region rast='+str(options['region'])+' res='+str(options['resolution'])+' -ap --verbose >> '+log_file
        try:
            out=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
        except subprocess.CalledProcessError as err:
            logger.error("Setting domain failed with error %s"%err)
    elif step == 'check_tile':
        #cmd='echo "call check_tile\n" >> '+log_file+';g.list ras | grep -c '+tile_data['surrounding_tile']+' >> '+log_file
        cmd='echo "call check_tile\n" >> '+log_file+';g.list ras >> '+log_file
        logger.info("Checking tile %s"%str(tile_data['surrounding_tile']))
        #this must return zero if tile is there
        try:
            out=subprocess.check_output(cmd,shell=True)
            #logger.debug("Answer from check_tile: %s"%out)
            return out
        except subprocess.CalledProcessError as err:
            logger.error("Checking tile failed with error %s"%err)
    elif step == 'import_tile':
        logger.info("Importing file %s"%str(tile_data['tif_file']))
        logger.info("Output tile %s"%str(tile_data['surrounding_tile']))
        cmd='echo "call import_tile\n" >> '+log_file+';r.in.gdal in='+tile_data['tif_file']+' out='+tile_data['surrounding_tile']+' -o memory=150 --verbose >> '+log_file
        try:
            out=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
            #logger.debug(out)
        except subprocess.CalledProcessError as err:
            logger.error("Importing tif file %s failed with error %s"%(tile_data['tif_file'],err))
    elif step == 'set_region':
        logger.info("Setting region %s"%str(tile_data['region']))
        cmd='echo "call set_region\n" >> '+log_file+';g.region rast='+tile_data['region']+' res='+options['resolution']+' -ap --verbose >> '+log_file
        try:
            out=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
        except subprocess.CalledProcessError as err:
            logger.error("Setting region %s failed with error %s"%(tile_data['region'],err))
    elif step == 'set_patch':
        logger.info("Setting patch %s"%str(tile_data['region']))
        cmd='echo "call set_patch\n" >> '+log_file+';r.patch input='+tile_data['region']+' output=work_domain --overwrite --verbose >> '+log_file
        try:
            out=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
        except subprocess.CalledProcessError as err:
            logger.error("Setting region %s failed with error %s"%(tile_data['region'],err))
    elif step == 'calc_horizon':
        logger.info(f"call horizon calculation for {tile_data['coordinates_horizon']}")
        cmd='r.horizon -d elevation=work_domain step='+options['horizonstep']+' maxdistance='+options['maxdistance']+' coordinates='+str(tile_data['coordinates_horizon'])+' > '+tile_data['out_file']
        #cmd='echo "call horizon\n" >> '+log_file+';r.horizon -d elevation=work_domain step='+options['horizonstep']+' maxdistance='+options['maxdistance']+' coordinates='+str(tile_data['coordinates_horizon'])+' >> '+log_file
        try:
            out=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
        except subprocess.CalledProcessError as err:
            logger.error("calc_horizon failed with error %s"%(err))
    elif step == 'cleanup':
        logger.info("Cleanup region before processing next station")
        cmd='g.remove -f type=raster name=work_domain --verbose'
        try:
            out=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
        except subprocess.CalledProcessError as err:
            logger.error("clean_up failed with error %s"%(err))

def calc_shadows(stretch_data,tiles_needed,shpars,out_dir,options):
    '''
    Go through list of stations and calculate
    shadows. Calls grass utilities in the process.
    This replaces the main bash script developed by Kai
    '''
    #This loop runs through all the files in the selected list
    for tile in stretch_data['tile'].values:
        logger.info("tile: %s "%tile)
        #Tiles surrounding the tile where this stations sits on:
        logger.info(f"calc_shadows: all tiles needed: {tiles_needed}")
        select_surrounding_tiles = tiles_needed[tiles_needed['station_tile'] == tile]
        logger.info("surrounding tiles selected")
        logger.info(select_surrounding_tiles['surrounding_tile'])
        ntiles=select_surrounding_tiles.shape[0] # This MUST be 9!
        #import the surrounding tiles into grass
        tile_data={}
        region_tiles=[]
        for i,stile in enumerate(select_surrounding_tiles['surrounding_tile'].values):
            logger.info("Doing surr. tile %s"%stile)
            tif_file=select_surrounding_tiles['tif_file'].values[i]
            tile_data['surrounding_tile'] = stile
            tile_data['tif_file'] = tif_file
            #NOTE: if this command fails then importing should not proceed
            check_tile=call_grass('check_tile',shpars,tile_data)
            #print("check_tile answer %s"%check_tile.decode("utf-8"))
            call_grass('import_tile',shpars,tile_data)
            region_tiles.append(stile)
        #define region
        logger.info("Establishing working domain")
        tile_data={}
        region=','.join(region_tiles)
        tile_data['region']=region
        #establish the working domain
        call_grass('set_region',shpars,tile_data)
        call_grass('set_patch',shpars,tile_data)
        tile_data={}
        #TEST: I was using here set(select_surrounding_tiles['coords'].values)
        #BUT: This will ignore tiles which contain a station
        # with the same tile but different names. Should I redo
        # the (wasted) calculation??
        for stretch in set(select_surrounding_tiles['coords'].values):
        #for stretch in select_surrounding_tiles['coords'].values:
            print("coords in surrounding tiles %s"%stretch)
            station_id=stretch.split('|')[2] 
            county=stretch.split('|')[3]
            roadsection=stretch.split('|')[4]
            tile_data['coordinates_horizon']=stretch.split('|')[0]+','+stretch.split('|')[1]
            tile_data['out_file']=os.path.join(out_dir,'_'.join(['lh',county,station_id,roadsection])+'.txt')
            print("Saving this id %s"%'_'.join([county,station_id,roadsection]))
            tile_data['station_id']=station_id
            call_grass('calc_horizon',shpars,tile_data)
        #when there is more than one coordinate do this after the loop    
        call_grass('cleanup',shpars,tile_data)    
            #call_grass('cleanup',shpars,tile_data)
            #logger.info("Saving shadow data in sqlite file")
            #save_dbase(tile_data,options)




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
    print("calc_tiles: selecting here the tile list for")
    print(stretchlist)
    tiles_list=OrderedDict()
    #tiles_list_long=OrderedDict()
    inserted_tiles=[]
    for k,stretch in stretchlist.iterrows():
        #Crude way to insert the station information
        #NOTE: the keys of the returned dictionary
        #will be based on the tiles only, hence
        #any repeated tiles for stations with different
        #sensors and slightly different coordinates
        #will be ignored below
        insert='|'.join([str(stretch['easting']),str(stretch['norting']),str(stretch['county']),str(stretch['station']),str(stretch['roadsection'])])
        stretch_east=float(stretchlist['easting'][k])
        stretch_nort=float(stretchlist['norting'][k])
        stretch_tile = str(int(stretch_nort/1000))+'_'+str(int(stretch_east/1000))
        try:
            if not isinstance(tiles_list[stretch_tile], list):
                pass
        except:
                tiles_list[stretch_tile] = []
                st_info = "_".join([str(stretch['county']),
                            str(stretch['station']),
                            str(stretch['roadsection'])])
                print(stretch_tile+"_"+st_info)
                #tiles_list_long[stretch_tile+"_"+st_info] = []
        print(f"Inserting {insert} into {stretch_tile}")       
        tiles_list[stretch_tile].append(insert)
        #tiles_list_long[stretch_tile+"_"+st_info].append(insert)
    print("List before passing over dict")
    print(tiles_list)
    #print(tiles_list_long)
    return tiles_list

def read_tif_list(tfile):
    tif_list=np.loadtxt(tfile,delimiter=' ',dtype=str)
    return tif_list


def loop_tilelist(list_tiles, tif_files,tif_dir):
    '''
    Calculates list of tif_files needed by the list of tiles
    Returns dataframe with necessary tiles and tif files
    '''
    tileside=1
    mindist=1
    maxdistance=1000
    dist=maxdistance / 1000
    tiles=OrderedDict()
    files=OrderedDict()
    ctiles_list=[]
    tiles_list=[]
    files_list=[]
    coords_list=[]
    for tkey in list_tiles.keys():
        #tiles_list=[]
        #files_list=[]
        east = int(tkey.split('_')[1])
        north = int(tkey.split('_')[0])
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
                #tiles_list.append('_'.join([str(sw_corner_north), str(sw_corner_east)]))
                #files_list.append(os.path.join(tif_dir,tfile))
                #ctiles_list.append(tkey)
                #coords_list.append(list_tiles[tkey][0]) # Why am I appending only the first coordinate only?? CHANGE: 20210924. Also 3 lines above
                #One tile might contain more than one station
                for coordinate in list_tiles[tkey]:
                    ctiles_list.append(tkey)
                    tiles_list.append('_'.join([str(sw_corner_north), str(sw_corner_east)]))
                    files_list.append(os.path.join(tif_dir,tfile))
                    coords_list.append(coordinate)
    #Make a dataframe containing arrays: ctiles_list, tiles_list, files_list, coords_list
    data = pd.DataFrame({'station_tile':ctiles_list,'surrounding_tile':tiles_list,
        'tif_file':files_list,'coords':coords_list})
    print("loop_tilelist: before passing data to be used by calc_shadows")
    print(data)
    return data
    #return tiles, files

def save_dbase(tile_data,options,ofile="station_shadows.sqlite"):
    '''
    save the results in an sqlite file
    '''
    ifile=tile_data['out_file']
    if not os.path.isfile(ofile):
        create_dbase_shadows(tile_data,options,ofile)
    else:
        update_dbase_shadows(tile_data,options,ofile)

def create_dbase_shadows(tile_data,options,ofile):
    '''
    Create first instance of database
    '''
    ifile=tile_data['out_file']
    #cols: azimuth, horizon_height
    data=pd.read_csv(ifile,index_col=False)
    #create a column with the values of the station, resol and other details
    data['station']=[tile_data['station_id']]*data.shape[0]
    data['resolution']=[options['resolution']]*data.shape[0]
    data['maxdistance']=[options['maxdistance']]*data.shape[0]
    data['horizonstep']=[options['horizonstep']]*data.shape[0]
    con = sqlite3.connect(ofile)
    data.to_sql('station_shadows',con,if_exists="append", index=False)
    con.close()

def update_dbase_shadows(tile_data,options,ofile):
    '''
    Update existing database
    '''
    #read old database
    print("updating database")
    con=sqlite3.connect(ofile)
    sql_command = "SELECT * FROM station_shadows"
    #cols: azimuth, horizon_height, station, resolution, horizon_step,maxdistance
    data_old=pd.read_sql(sql_command, con)
    #read new data produced by grass
    ifile=tile_data['out_file']
    data_new=pd.read_csv(ifile,index_col=False)
    #create a column with the values of the station, resol and other details
    data_new['station']=[tile_data['station_id']]*data_new.shape[0]
    data_new['resolution']=[options['resolution']]*data_new.shape[0]
    data_new['maxdistance']=[options['maxdistance']]*data_new.shape[0]
    data_new['horizonstep']=[options['horizonstep']]*data_new.shape[0]
    #write new data to database
    data_new.to_sql('station_shadows',con,if_exists="append", index=False)
    con.close()

