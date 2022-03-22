"""
Read the DANRA files to extract old data for 
a given gribcode
Data is in one variable per day, with all timestamps in the file
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
datapath="/tmp"

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
            "gust_u_component":
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
        this_date=sys.argv[4][0:8]
        this_cycle=sys.argv[4][8:10]
        print(f"Using {findLat} {findLon} on {this_date}{this_cycle}")
    else:
        print(f"Not enough parameters: {sys.argv}")
        sys.exit(1)

    gribpath=os.path.join(datapath,this_date)
    year = this_date[0:4]
    month = this_date[4:6]
    day = this_date[6:8]
    hour = this_date[8:10]
    hours_avail = [str(i).zfill(2) for i in range(0,19)]

    for this_code in codes.keys():
        indicatorOfParameter = codes[this_code]["indicatorOfParameter"]
        levelType = codes[this_code]["levelType"]
        level = codes[this_code]["level"]
        timeRangeIndicator = codes[this_code]["timeRangeIndicator"]
        station=OrderedDict()
        for key in ["date","value"]:
            station[key] = []
        f = os.path.join(gribpath,
                "_".join(["DKREA_PRODYEAR",year,month,day,str(indicatorOfParameter),str(levelType),str(level),str(timeRangeIndicator),"FC33hr"]))

        if os.path.isfile(f):
            print("-----------------")
            print(f"Reading file: {f}")
            print("-----------------")

            gribfile = os.path.join(gribpath,f)
            g = grib(gribfile=gribfile,indicatorOfParameter=indicatorOfParameter,level=level,levelType=levelType,timeRangeIndicator=timeRangeIndicator,stationId=stationId)
            #all_data=g.get_data()
            for fhour in hours_avail:
                timestamp=year+month+day+hour+str(this_cycle)+fhour
                print(f"Looking for {timestamp}")
                data=g.get_data_loc_fstep(findLat,findLon,timestamp)
                times=g.get_times()
                if len(data["values"].keys()) > 0:
                    fcstep = data["fcstep"]
                    for key in data["values"].keys():
                        station["value"].append(data["values"][key])
                        station["date"].append(timestamp)
        else:
            print(f"{f} not available!")
            continue
        df=pd.DataFrame(station)
        #out="_".join([stationId,str(indicatorOfParameter),str(levelType),str(level),this_date])+".csv"
        out="_".join([stationId,this_code,str(level),this_date+this_cycle])+".csv"
        df.sort_values(inplace=True,by=["date"])
        df.to_csv(out,index=False)
