# Importing the FastApi class
from fastapi import FastAPI
import pandas as pd
import numpy as np
import sys
import sqlite3
import json

# Creating an app object
app = FastAPI()

# Post -- > Create new prediction
@app.put("/coordinates", tags=["COORDINATES"])
async def get_user_input(body: dict) -> dict:
    for key in body.keys():
        user_input[key] = body[key]
    return body

@app.post("/shadows", tags=['SHADOWS'])
async def search_station() -> dict:
    return {"shadows": prediction}

@app.get("/shadows", tags=['ALL_SHADOWS'])
async def print_all_data() -> dict:
    return {"shadows": all_stations}

#--------------------------------------------------


DBASE={'road_stretch':"./app/shadows_road_stretches.db",
       'road_station':"./app/noshadows_daily_upates.db"}

def standardToCompass(angle):
    """
    Convert angle measured from +X axis counterclockwise
    to angle measured clockwise from +Y axis
    This only works for *wind directions*!
    """
    compass = 90 - angle
    if compass < 0:
        compass = compass + 360
    compass = compass + 180
    if compass >= 360:
        compass = compass - 360
    #Up to here the result is ok for wind fetch,
    # but I want just the angle
    compass = compass + 180
    #reset to 0 if it goes above 360
    if compass >= 360:
        compass = compass - 360
    return compass

def reformat(stationID,dbase):
    station=str(stationID)[0:4]
    sensor="0"
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    find_station = f"SELECT * FROM shadows WHERE (stationID={stationID});"
    df=pd.read_sql(find_station, conn)
    station_data=[]
    if not df.empty:
        angles = df.azimuth.to_list()
        shadows = df.horizon_height.to_list()
        angles_rot=[]
        for angle in angles:
            convAngle = standardToCompass(angle)
            #print(f"converting angle {angle} to {convAngle}")
            angles_rot.append(convAngle)
        s = np.array(angles_rot)
        sort_index = np.argsort(s)
        shadows_order = [str(shadows[i]) for i in sort_index]
        angles_order = [angles_rot[i] for i in sort_index]
        station_data.append(",".join([station,sensor]+shadows_order))
        station_data.append("\n")
    return station_data



def search_by_coords(coords,dbase):
    """
    Search by coordinates. In this case
    it is easier to use the search function in the dataframe
    """
    lat=float(coords.split(",")[0])
    lon=float(coords.split(",")[1])
    #lat_short=Decimal(lat) % 1
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    com = f"SELECT * FROM roadstations;"
    df=pd.read_sql(com, conn)
    df["distance"] = [np.sqrt((la-lat)*(la-lat) + (lo-lon)*(lo-lon)) for la,lo in zip(df.lat.values,df.lon.values)]
    idx = df.distance.idxmin()
    station = df.stationID.iloc[idx]
    closest_lat = df.lat.iloc[idx]
    closest_lon = df.lon.iloc[idx]
    print(f"Closest match to {lat},{lon} is {closest_lat},{closest_lon}: {station}")
    data=reformat(station,dbase)
    coords_found = ",".join([str(closest_lat),str(closest_lon)])
    return data,coords_found

def search_by_station(stationID,dbase):
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    find_station = f"SELECT * FROM shadows WHERE (stationID={stationID});"
    df=pd.read_sql(find_station, conn)
    if df.empty:
        print("Station not found")
    else:
        data=reformat(stationID,dbase)
        return data

def print_dbase(dbase):
    find_station = f"SELECT * FROM roadstations;"
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    df=pd.read_sql(find_station, conn)
    dump=[]
    for stationID,lat,lon in zip(df.stationID,df.lat,df.lon):
        dump.append({"stationID":stationID,"lat":lat,"lon":lon})
    return dump

#if station is not None:
#    print(f"Looking for station {station}")
#    data=search_by_station(station,dbase)
#    print("Shadow data")
#    print("".join(data))
#elif coords is not None:
#    print(f"Looking for coordinates {coords}")
#    data=search_by_coords(coords,dbase)
#    print("Shadow data")
#    print("".join(data))
#else:
#    print("Please provide either station or coordinates")
#    sys.exit(1)


#Filling up this with some default values

user_input = {
"lat": 55,
"lon":12,
"dbase": "road_stretch"
    }

#model = get_model()
#y_pred = np.exp(model.predict(features)) #remember I trained it for log(Appl)
coords = ",".join([str(user_input["lat"]),str(user_input["lon"])])
shadows,coords_found=search_by_coords(coords,DBASE[user_input["dbase"]])
all_stations = print_dbase(DBASE[user_input["dbase"]])
#print(all_stations)
#
#prediction = [ {
#         "features": user_input,
#         "Appliances": float(y_pred) }
#]
prediction = [ {"features":user_input,
                "Shadows":"".join(shadows),
                 "Closest coordinates":coords_found} ]

all_stations = {"Database selected":DBASE[user_input["dbase"]],
                "All stations available":all_stations}
