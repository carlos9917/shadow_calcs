"""
Read the cloud data from the SAF files in grib format
Example file name: SAFNWC_MSG_CT_area_FM3_202202011300
"""
import eccodes as ecc
from collections import OrderedDict
import eccodes as ecc
import numpy.ma as ma
from datetime import datetime
import os
import sys
from collections import OrderedDict
import pandas as pd

sys.path.insert(0, os.path.abspath('../'))
from grib_utils.gribio import grib as grib

cloud_cover = {1:"cloud free land",
               2: "cloud free sea",
               3: "snow over land",
               4: "sea ice",
               5: "very low clouds",
               6: "low clouds",
               7: "mid-level clouds",
               8: "high opaque clouds",
               9: "very high opaque clouds",
               10: "fractional clouds",
               11: "high semitransparent thin clouds",
               12: "high semitransparent moderately thick clouds",
               13: "high semitransparent thick clouds",
               14: "high semitransparent above low or medium clouds",
               15: "high semitransparent above snow/ice",
               16: "high semitransparent thin cirrus",
               17: "high semitransparent thick cirrus",
               18: "high semitransparent cirrus above low or medium level clouds",
               19: "fractional clouds",
               20: "undefined"}

if __name__== "__main__":
    station=OrderedDict()
    for key in ["lat","lon","date","cloudiness","description"]:
        station[key] = []
    indicatorOfParameter =171 #this is for CMa
    indicatorOfParameter =172 #this is for CT
    levelType=105
    level=0
    timeRangeIndicator=0

    gribpath="/data/users/cap/glatmodel/cloud_data/cloud_type"
    files=os.listdir(gribpath)

    if len(sys.argv) == 1:
        print("Please provide lat, lon and date")
        sys.exit(1)
    elif len(sys.argv) == 4:
        findLat=float(sys.argv[1])
        findLon=float(sys.argv[2])
        this_date=sys.argv[3]
        print(f"Using {findLat} {findLon} on {this_date}")
    else:
        print(f"Not enough parameters: {sys.argv}")
        sys.exit(1)

    stationId = "Test" #Not important here
    for f in files:
        if f.startswith("SA") and this_date in f:
            print("-----------------")
            print(f"Reading file: {f}")
            print("-----------------")
            split_time=f.split("_")[-1]
            year = int(split_time[0:4])
            month = int(split_time[4:6])
            day = int(split_time[6:8])
            hour = int(split_time[8:10])
            minute = int(split_time[10:12])

            gribfile = os.path.join(gribpath,f)
            g = grib(gribfile=gribfile,indicatorOfParameter=indicatorOfParameter,level=level,levelType=levelType,timeRangeIndicator=timeRangeIndicator,stationId=stationId)
            data=g.get_data_loc(findLat,findLon)
            times=g.get_times()
            if len(data["values"].keys()) > 0:
                try: #sometimes not findind the correct time to the minute?
                    time_found=datetime(year, month, day, hour, minute)
                    cloudy = int(data["values"][time_found])
                    station["date"].append(datetime.strftime(time_found,"%Y%m%d%H%M%S"))
                except:    
                    time_found=datetime(year, month, day, hour, 0)
                    cloudy = int(data["values"][time_found])
                    station["date"].append(datetime.strftime(time_found,"%Y%m%d%H%M%S"))
                print(f"Using {time_found} and cloudyness: {cloudy}")
                station["cloudiness"].append(cloudy)
                station["description"].append(cloud_cover[cloudy])
                station["lat"].append(findLat)
                station["lon"].append(findLon)
    df=pd.DataFrame(station)
    df.sort_values(inplace=True,by=["date"])
    out="data_"+str(this_date)+".csv"
    print(f"Writing {out}")
    df.to_csv(out,index=False)
