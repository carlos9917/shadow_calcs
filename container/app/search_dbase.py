import sys
import pandas as pd
import sqlite3
import numpy as np
DBASE="shadows_road_stretches.db" #default

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
        #This is just for debugging
        #print("Ordered angles and shadows")
        #print_df = pd.DataFrame({"angle":angles,
        #                             "shadow": shadows,
        #                             "angle_rotated": angles_rot,
        #                             "angle_met": angles_order,
        #                             "shadow_met": shadows_order})
        #print(print_df.to_markdown())
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
    #find_station = f"SELECT * FROM roadstations WHERE (lat={lat} AND lon={lon});"
    com = f"SELECT * FROM roadstations;"
    df=pd.read_sql(com, conn)
    df["distance"] = [np.sqrt((la-lat)*(la-lat) + (lo-lon)*(lo-lon)) for la,lo in zip(df.lat.values,df.lon.values)]
    idx = df.distance.idxmin()
    station = df.stationID.iloc[idx]
    closest_lat = df.lat.iloc[idx]
    closest_lon = df.lon.iloc[idx]
    print(f"Closest match to {lat},{lon} is {closest_lat},{closest_lon}: {station}")
    data=reformat(station,dbase)
    return data

def search_by_station(stationID,dbase):
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    find_station = f"SELECT * FROM shadows WHERE (stationID={stationID});"
    df=pd.read_sql(find_station, conn)
    if df.empty:
        print("Station not found")
    else:
        #data = df[["azimuth",  "horizon_height"]]
        #print(data)
        data=reformat(stationID,dbase)
        return data



if __name__=="__main__":
    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description='''
            Example usage: python3 search_dbase.py -station 2038,0,0 ''',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-station',help='station to search (long name)',
            metavar="Provide name in format station+sensor1+sensor2+sensor3 with sensors in 2 digits with sensors in 2 digits ex: 1000 00 00 00",
                        type=str,
                        default=None,
                        required=False)

    parser.add_argument('-coords',help='coords to search, separated by commas',
                        type=str,
                        default=None,
                        required=False)

    parser.add_argument('-dbase',help='sql database',
                        type=str,
                        default=DBASE,
                        required=False)



    args = parser.parse_args()
    station = args.station
    dbase = args.dbase
    coords = args.coords
    if station is not None:
        print(f"Looking for station {station}")
        data=search_by_station(station,dbase)
        print("Shadow data")
        print("".join(data))
    elif coords is not None:
        print(f"Looking for coordinates {coords}")
        data=search_by_coords(coords,dbase)
        print("Shadow data")
        print("".join(data))
    else:
        print("Please provide either station or coordinates")
        sys.exit(1)

