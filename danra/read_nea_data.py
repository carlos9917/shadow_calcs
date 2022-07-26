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
    codes={
            "u_wind_component": 
                 {"indicatorOfParameter":33,
                  "levelType": 105,
                  "level": 50,
                  "timeRangeIndicator":0
                  },
            "v_wind_component": 
                  {"indicatorOfParameter":34,
                  "levelType": 105,
                  "level": 50,
                  "timeRangeIndicator":0
                  },
            "u_wind_component": 
                 {"indicatorOfParameter":33,
                  "levelType": 105,
                  "level": 100,
                  "timeRangeIndicator":0
                  },
            "v_wind_component": 
                  {"indicatorOfParameter":34,
                  "levelType": 105,
                  "level": 100,
                  "timeRangeIndicator":0
                  },
            "WDIR10m": 
                 {"indicatorOfParameter":31,
                  "levelType": 105,
                  "level": 10,
                  "timeRangeIndicator":0
                  },
            "U10m": 
                  {"indicatorOfParameter":32,
                  "levelType": 105,
                  "level": 10,
                  "timeRangeIndicator":0
                  },
            "gust_u_component":
                  {"indicatorOfParameter":162,
                  "levelType": 105,
                  "level": 10,
                  "timeRangeIndicator":2
                  },
            "gust_v_component":
                  {"indicatorOfParameter":163,
                  "levelType": 105,
                  "level": 10,
                  "timeRangeIndicator":2
                  },
            "T2m":
                  {"indicatorOfParameter":11,
                  "levelType": 105,
                  "level": 2,
                  "timeRangeIndicator":0
                  },
            "mslp":
                  {"indicatorOfParameter":1,
                  "levelType": 103,
                  "level": 0,
                  "timeRangeIndicator":0
                  },
            "pressure":
                  {"indicatorOfParameter":1,
                  "levelType": 105,
                  "level": 0,
                  "timeRangeIndicator":0
                  },
            }
    #indicatorOfParameter =33
    #levelType=105
    #level=100
    #timeRangeIndicator=0
    

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
