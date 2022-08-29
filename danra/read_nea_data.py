"""
Read the nea operational data and extract desired date
Data is organized on one file per timestep for each cycle.
Individual files with name XXX contain only one timestamp
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
#Path for the NEA data
datapath="/data/projects/nckf/danra/storms/NEA"

if __name__== "__main__":
    #List of codes to use.
    # Note that NEA does not include the U10m variable,
    # so the data for U,V at 10m is extracted
    # and the U10m is calculated at the end
    from grib_codes_list import codes

    if len(sys.argv) == 1:
        print("Please provide station,lat,lon and date")
        sys.exit(1)
    elif len(sys.argv) == 5:
        stationId=sys.argv[1]
        findLat=float(sys.argv[2])
        findLon=float(sys.argv[3])
        this_date=sys.argv[4]
        print(f"Using {findLat} {findLon} on {this_date}")
    else:
        print(f"Not enough parameters: {sys.argv}")
        sys.exit(1)

    gribpath=os.path.join(datapath,this_date)
    files=os.listdir(gribpath)
    if len(files) == 0:
        print(f"No data for {this_date}!")
        sys.exit(1)

    for this_code in codes.keys():
        indicatorOfParameter = codes[this_code]["indicatorOfParameter"]
        levelType = codes[this_code]["levelType"]
        level = codes[this_code]["level"]
        timeRangeIndicator = codes[this_code]["timeRangeIndicator"]
        station=OrderedDict()
        for key in ["date","value"]:
            station[key] = []
        for f in files:
           if len(f) == 3: #only reading hourly data
               gribfile = os.path.join(gribpath,f)
               print("-----------------")
               print(f"Reading file: {gribfile}")
               print("-----------------")

               g = grib(gribfile=gribfile,indicatorOfParameter=indicatorOfParameter,level=level,levelType=levelType,timeRangeIndicator=timeRangeIndicator,stationId=stationId)
               data=g.get_data_loc(findLat,findLon)
               #times=g.get_times()
               if len(data["values"].keys()) > 0:
                   for key in data["values"].keys():
                       this_time=datetime.strftime(key,"%Y%m%d%H")+str(int(f)).zfill(2)
                       print(f"Saving {this_time}")
                       station["value"].append(data["values"][key])
                       station["date"].append(this_time)
               else:
                   print(f"WARNING: No data for {this_date} in {gribfile} for {this_code}")
                   print(f"Jumping this hour")
                   continue
        df=pd.DataFrame(station)
        #out="_".join([stationId,str(indicatorOfParameter),str(levelType),str(level),this_date])+".csv"
        out="_".join([stationId,this_code,str(level),this_date])+".csv"
        df.sort_values(inplace=True,by=["date"])
        df.to_csv(out,index=False)

    #extra processing to create the u10     
    #just produce the magnitude of u,v at 10 m
    import numpy as np
    dir_path="."
    from pathlib import Path
    for u_file in Path(dir_path).glob('*_u10_wind_*.csv'):
        if not "gust" in str(u_file):
            v_file = str(u_file).replace("u10_wind","v10_wind")
            #print(v_file)
            if os.path.isfile(v_file):
                print(f"Using {u_file} and {v_file} to calculate U10m")
                df_u = pd.read_csv(u_file)
                df_v = pd.read_csv(v_file)
                dates = df_u["date"].to_list()
                u = df_u["value"].to_list()
                v = df_v["value"].to_list()
                u10 = []
                for k,u_k in enumerate(u):
                    u10.append(np.sqrt(u_k*u_k + v[k]*v[k]))
                df = pd.DataFrame({"date":dates,
                                    "value":u10})
                ofile=v_file.replace("v10_wind_10","U10m")
                print(f"Writing to {ofile}")
                df.to_csv(ofile,index=False)
    from calc_wdir import calc_wdir10
    calc_wdir10(dir_path)
