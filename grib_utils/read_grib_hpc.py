"""
Example script to read a few files, check data on a particular lat lon
"""
import eccodes as ecc
from collections import OrderedDict
import eccodes as ecc
import numpy.ma as ma
from datetime import datetime
import os
from gribio import grib as grib
import sys
from pathlib import Path
import glob

if __name__== "__main__":

    indicatorOfParameter =171
    levelType=105
    level=0
    timeRangeIndicator=0
    gribpath="/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_radar" 
    gribpath = "/devdata/glatdev/R0T/cloud/"#SAFNWC_MSG_CMa_area_FM3*20220204*
    today_str = datetime.strftime(datetime.today(),"%Y%m%d")
    today_str = "20220202"
    print(today_str)
    files=[]; sizes=[]
    #for filename in glob.iglob(gribpath):
    #    print(filename)
    #    if today_str in filename:
    #        allfiles.append(filename)
    for file_path in Path(gribpath).glob('*area_FM3*'+today_str+'*'): 
        files.append(str(file_path))
        sizes.append(file_path.stat().st_size/(1024*1024*1024))
        #print(file_path)
    #print(files)
    print(sum(sizes))
    print(len(files))
    files=os.listdir(gribpath)

    findLat = 55.995613
    findLon = 12.486561
    stationId = "Test"
    #print(files)
    for f in files:
        if f.startswith("SA"):
            gribfile = os.path.join(gribpath,f)
            print("-----------------")
            print(f"Reading file: {gribfile}")
            print("-----------------")
            g = grib(gribfile=gribfile,indicatorOfParameter=indicatorOfParameter,level=level,levelType=levelType,timeRangeIndicator=timeRangeIndicator,stationId=stationId)
            #g.check_codes()
            data=g.get_data()
            #data=g.get_data_loc(findLat,findLon)
            #get_closest = g.print_all_data_loc(findLat,findLon)
            #print(get_closest)
            times=g.get_times()
            print(f"Times: {times}")
            if len(data["values"].keys()) > 0:
                #print(data["values"][datetime(2022, 1, 31, 0, 0)])
                print(data["values"].keys())
            #print(f'Keys in data.values: {data["values"].keys()}')
            #check_data = data["values"][datetime(2022, 1, 31, 0, 0)]
            #Taking the first one, since it is the first level:
            #this_value= get_closest[0]
            #if "CT" in f:
            #    print(f"Checking {f}")
            #    g = grib(gribfile=gribfile,indicatorOfParameter=172,level=0,levelType=105,timeRangeIndicator=0,stationId=stationId)
            #    #g.check_codes()
            #    data=g.get_data()
            #    #get_closest = g.get_latlon(findLat,findLon)
            #    import pdb
            #    pdb.set_trace()
            #    #print(data["values"])
    #interpolate to a point

    #nx,ny = g.get_dims()
    #print(data)
