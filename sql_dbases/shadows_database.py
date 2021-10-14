# Import module
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
        lat FLOAT,
        lon FLOAT
            )
    """
    
    #Cotains only azimuth and shadow for particular station
    create_shadows = """
    CREATE TABLE IF NOT EXISTS shadows ( 
           stationID INTEGER NOT NULL PRIMARY KEY,
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

def update_shadows(dbase,coordinates,datadir):
    """
    Update the shadow data from each station
    based on the data in datadir (the directory with the shadows)
    """
    pass
    station_shadows= os.listdir(datadir)    
    station_shadows = [st for st in station_shadows if st.startswith("lh")]
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()

def update_settings(dbase,datadir):
    """
    Updates the settings database
    All information is taken from the directory name:
    lh_maxdistance_resolution_horizonstep_2digits
    """
    con = sqlite3.connect(dbase)
    maxdistance = datadir.split("/")[-1].split("_")[1]
    resolution = datadir.split("/")[-1].split("_")[2]
    horizonstep = datadir.split("/")[-1].split("_")[3]
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
    

def get_latlon(coords,stationID,stationType):
    """
    Get latitude and longitude for a stationID
    @coords: dataframe with the station data
    @stationType: road_stretch for the old stations
                 noshadows for the new stations
    @stationID: dict with station data
    """
    # Old convention
    # station name lon lat
    # 1000,"Kvistgård",12.486561,55.995613
    if stationType=="road_stretch":
        station = stationID["station"]
        get_data=coords[(coords.station == station) ]
        if not get_data.empty:
           lat = get_data.lat.values[0]
           lon = get_data.lat.values[0]
           return lat,lon
        else:
           print(f"{station} not found in lat/lon list")
    #New convention
    #station,name,sensor1,sensor2,sensor3,lon,lat
    #2038,"Sønder Jernløse",0,0,0,11.64767,55.657359
    elif stationType=="noshadows":
        station = stationID["station"]
        sensor1 = stationID["sensor1"]
        sensor2 = stationID["sensor2"]
        sensor3 = stationID["sensor3"]
        get_data=coors[(coords.station == station) & \
                       (coords.sensor1 == sensor1) & \
                       (coords.sensor2 == sensor2) & \
                       (coords.sensor3 == sensor3)]
        if not get_data.empty:
           lat = get_data.lat.values[0]
           lon = get_data.lat.values[0]
           return lat,lon
        else:
           print(f"{station} not found in lat/lon list")
    
def update_roadstations(dbase,coords,datadir):
    """
    Update the road stations database
    This needs the additional information from the csv list
    with the lat and lon coordinates of each station
    """
    station_shadows= os.listdir(datadir)    
    station_shadows = [st for st in station_shadows if st.startswith("lh")]
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    for station_data in station_shadows:
        df = pd.read_csv(os.path.join(datadir,station_data))
        #for the old data I was using road_station_county
        road = station_data.split("_")[1] 
        station = station_data.split("_")[2]
        county = station_data.split("_")[3].replace(".txt","")
        sensor3 = 0
        stationID = {"station":int(station)}
        lat,lon = get_latlon(coords,stationID,"road_stretch") #50.
        #lon = 12.
        stationID = str(station)+str(road).zfill(2)+str(county).zfill(2)+str(sensor3).zfill(2)
        #Update station list
        #data = cursor.execute('''SELECT * FROM roadstations''')
        #com = '''UPDATE stationID  = '''+stationID+";"
        #condition = '''WHERE NOT EXISTS (SELECT * FROM roadstations WHERE stationID = )'''+stationID+","+"lat = "+str(lat)+", lon = "+str(lon)+");"
        find_station = "SELECT * FROM roadstations WHERE (stationID = "+stationID+","+"lat = "+str(lat)+", lon = "+str(lon)+");"
        find_station = f"SELECT * FROM roadstations WHERE (stationID={stationID} AND lat={lat} AND lon={lon});"
        #check if the data is already there
        entry = cursor.execute(find_station)
        if len(cursor.fetchall()) == 0:
        #if entry is None:
            print(f"Inserting {station} {county} {road}")
            #since I already checked condition above, no nee dto use condition here
            #condition = f"WHERE NOT EXISTS (SELECT * FROM roadstations WHERE stationID = {stationID} AND lat = {lat} AND lon = {lon});"
            com = '''INSERT INTO roadstations (stationID, lat, lon) VALUES ('''+stationID+","+str(lat)+","+str(lon)+") " #+condition
            cursor.execute(com)
        else:
            print(f"entry for {station} {county} {road} found")
            #print(cursor.fetchall())
        #'''INSERT INTO EMPLOYEE(FIRST_NAME, LAST_NAME, AGE, SEX, INCOME)
        #VALUES ('Anand', 'Choubey', 25, 'M', 10000)''')


        #cursor.execute(com)
        conn.commit()
        #for azimuth,horizon in zip(df.azimuth,df.horizon_height):
    conn.close()
            

if __name__== '__main__':
    DBASE="shadows_road_stretches.db"
    tables = schema()
    #create_database(DBASE,tables)
    datapath = "/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/lh_500_0.4_11.25_00"
    update_database(DBASE,datapath)
