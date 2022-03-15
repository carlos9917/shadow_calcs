"""
Some utility functions for the shadows databases

""" 
import sqlite3
import os
import pandas as pd

def schema():
    """
    Define the schema.

    For new shadow stations stationID is a combination of station+sensor1+sensor2+sensor3
    Sensor numbers will have up to 2 digits, while stations have 4 digits
    Make a unique station name like: stationID = int(str(station)+str(sensor1).zfill(2)+str(sensor2).zfill(2)+str(sensor3).zfill(2))

    For old road-stretch stations the stationID is a combination of station,
    road and county (which I am currently setting to 00 in both cases)
    """
    create_stationlist = """
    CREATE TABLE IF NOT EXISTS roadstations (
        stationID INTEGER NOT NULL PRIMARY KEY,
        stationName TEXT,
        lat FLOAT,
        lon FLOAT
            )
    """
    
    #This table contains only azimuth and shadow for particular station
    #Note I am not defining any PRIMARY key in this table, since
    #that would make it difficult to update it. Not good practice,
    #but it works here
    
    create_shadows = """
    CREATE TABLE IF NOT EXISTS shadows ( 
           stationID INTEGER,
           azimuth FLOAT,
           horizon_height FLOAT
           )
    """
    
    #This one saves the settings for the GRASS horizon tool calculations
    create_settings = """
    CREATE TABLE IF NOT EXISTS horizon_settings (
         resolution FLOAT,
         maxdistance FLOAT,
         horizonstep FLOAT
         )
    """
    create_tables = {"roadstations":create_stationlist,
             "shadows": create_shadows,
             "settings": create_settings}

    return create_tables

def create_database(dbase,tables):
    """
    Create an empty database for the tables listed in tables
    """
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    for table in tables.keys():
        cursor.execute(tables[table])

def update_shadows(dbase,datapath,station_type):
    """
    Update the shadow data from each station
    based on the data in datapath (the directory with the shadows)
    """
    station_shadows= os.listdir(datapath)    
    #only select files that start with lh
    station_shadows = [st for st in station_shadows if st.startswith("lh")]
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    for station_data in station_shadows:
        df = pd.read_csv(os.path.join(datapath,station_data))
        if station_type == "road_stretch":
            #for the old data I was using road_station_county
            road = station_data.split("_")[1] 
            station = station_data.split("_")[2]
            county = station_data.split("_")[3].replace(".txt","")
            sensor3 = 0
            stationID = str(station)+str(road).zfill(2)+str(county).zfill(2)+str(sensor3).zfill(2)
        elif station_type == "noshadows":
            station = station_data.split("_")[1] 
            sensor1 = station_data.split("_")[2]
            sensor2 = station_data.split("_")[3].replace(".txt","")
            sensor3 = 0 #still not in use
            stationID = str(station)+str(sensor1).zfill(2)+str(sensor2).zfill(2)+str(sensor3).zfill(2)
        find_station = f"SELECT * FROM shadows WHERE (stationID={stationID});"
        entry = cursor.execute(find_station)
        if len(cursor.fetchall()) == 0:
            for azimuth,horizon_height in zip(df.azimuth.values,df.horizon_height.values):
                com = f"INSERT OR IGNORE INTO shadows (stationID, azimuth, horizon_height) VALUES ({stationID},{azimuth},{horizon_height});"
                cursor.execute(com)
        else:
            print(f"entry for {station} {county} {road} already in shadows ")
        conn.commit()
    conn.close()

def update_settings(dbase,datapath):
    """
    Updates the settings database
    All information is taken from the directory name:
    lh_maxdistance_resolution_horizonstep_2digits
    """
    con = sqlite3.connect(dbase)
    maxdistance = datapath.split("/")[-1].split("_")[1]
    resolution = datapath.split("/")[-1].split("_")[2]
    horizonstep = datapath.split("/")[-1].split("_")[3]
    cursor = con.cursor()
    com = "SELECT * FROM horizon_settings"
    cursor.execute(com)
    check_state = cursor.fetchall()
    if len(check_state) == 0:
        com = f"INSERT INTO horizon_settings (resolution, maxdistance, horizonstep) VALUES ({resolution},{maxdistance},{horizonstep})"
        cursor.execute(com)
    else:
        df=pd.read_sql(com, con) 
        com=f"UPDATE horizon_settings SET resolution = REPLACE(resolution, {df.resolution.values[0]}, {resolution});"
        cursor.execute(com)
        com=f"UPDATE horizon_settings SET maxdistance = REPLACE(resolution, {df.maxdistance.values[0]}, {maxdistance});"
        cursor.execute(com)
        com=f"UPDATE horizon_settings SET horizonstep = REPLACE(horizonstep, {df.horizonstep.values[0]}, {horizonstep});"
        cursor.execute(com)
    con.commit()
    con.close()
    

def get_latlon(coords,stationID,station_type):
    """
    Get latitude and longitude for a stationID.
    It also returns the station name
    @coords: dataframe with the station data
    @station_type: road_stretch for the old stations
                 noshadows for the new stations
    @stationID: dict with station data
    """
    # Old convention
    # station name lon lat
    # 1000,"Kvistgård",12.486561,55.995613
    if station_type=="road_stretch":
        station = stationID["station"]
        get_data=coords[(coords.station == station) ]
        if not get_data.empty:
           lat = get_data.lat.values[0]
           lon = get_data.lon.values[0]
           stationName = get_data.name.values[0]
           return lat,lon, stationName
        else:
           print(f"{station} not found in lat/lon list")
    #New convention
    #station,name,sensor1,sensor2,sensor3,lon,lat
    #2038,"Sønder Jernløse",0,0,0,11.64767,55.657359
    elif station_type=="noshadows":
        station = stationID["station"]
        sensor1 = stationID["sensor1"]
        sensor2 = stationID["sensor2"]
        sensor3 = stationID["sensor3"]
        get_data=coords[(coords.station == station) & \
                       (coords.sensor1 == sensor1) & \
                       (coords.sensor2 == sensor2) & \
                       (coords.sensor3 == sensor3)]
        if not get_data.empty:
           lat = get_data.lat.values[0]
           lon = get_data.lon.values[0]
           stationName = get_data.name.values[0]
           return lat,lon,stationName
        else:
           print(f"{station} not found in lat/lon list")
    
def update_roadstations(dbase,coords,datapath,station_type):
    """
    Update the "roadstations" table. This is just
    a list of the available stations. The information
    about station name is taken from the file name.
    This needs the additional information from the csv list
    with the lat and lon coordinates of each station
    """
    station_shadows= os.listdir(datapath)    
    station_shadows = [st for st in station_shadows if st.startswith("lh")]
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    for station_data in station_shadows:
        if station_type == "road_stretch":
            #for the old data I was using road_station_county
            road = station_data.split("_")[1] 
            station = station_data.split("_")[2]
            county = station_data.split("_")[3].replace(".txt","")
            sensor3=0
            st_dict = {"station":int(station)}
            lat,lon,stationName = get_latlon(coords,st_dict,station_type)
            stationID = str(station)+str(road).zfill(2)+str(county).zfill(2)+str(sensor3).zfill(2)
        elif station_type == "noshadows":
            #the new data follows convention station_sensor1_sensor2_sensor3
            station = station_data.split("_")[1] 
            sensor1 = station_data.split("_")[2]
            sensor2 = station_data.split("_")[3].replace(".txt","")
            sensor3 = 0 #still not in use
            st_dict = {"station":int(station),
                       "sensor1":int(sensor1),
                       "sensor2":int(sensor2),
                       "sensor3":int(sensor3) }
            lat,lon,stationName = get_latlon(coords,st_dict,station_type)
            stationID = str(station)+str(sensor1).zfill(2)+str(sensor2).zfill(2)+str(sensor3).zfill(2)
          
        #Update station list
        #This does not work, but in the end it is only the stationId and coordinates which are important
        #find_station = f"SELECT * FROM roadstations WHERE (stationID={stationID} AND lat={lat} AND lon={lon} AND stationName=('{str(stationName)})');"
        if "'" in stationName: stationName= stationName.replace("'","")
 
        find_station = f"SELECT * FROM roadstations WHERE stationID = {stationID} AND lat = {lat} AND lon = {lon} AND stationName = '{stationName}'"
        #find_station = f"SELECT * FROM roadstations WHERE (stationID={stationID} AND lat={lat} AND lon={lon});"
        #check if the data is already there
        print(find_station)
        entry = cursor.execute(find_station)
        if len(cursor.fetchall()) == 0:
            print(f"Inserting {stationID}")
            #since I already checked condition above, no nee dto use condition here
            #condition = f"WHERE NOT EXISTS (SELECT * FROM roadstations WHERE stationID = {stationID} AND lat = {lat} AND lon = {lon});"
            insert_row = ",".join([stationID,"'"+stationName+"'",str(lat),str(lon)])
            com = '''INSERT INTO roadstations (stationID, stationName, lat, lon) VALUES ('''+insert_row+") "
            cursor.execute(com)
        else:
            #print(f"entry for {station} {county} {road} already in roadstations ")
            print(f"entry for {stationID} already in roadstations ")
        conn.commit()
    conn.close()
            

if __name__== '__main__':
    DBASE="shadows_road_stretches.db"
    tables = schema()
    #create_database(DBASE,tables)
    datapath = "/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/lh_500_0.4_11.25_00"
    update_database(DBASE,datapath)
