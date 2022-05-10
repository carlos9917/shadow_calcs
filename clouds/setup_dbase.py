import sqlite3
import pandas as pd
import os
import sys

create_clouds = """
    CREATE TABLE IF NOT EXISTS clouds ( 
           stationID INTEGER,
           stationName TEXT,
           date TEXT,
           lat FLOAT,
           lon FLOAT,
           cloud INTEGER
           )
"""
DBASE="clouds.db"
def create_database(dbase,schema):
    """
    Create an empty database for the tables listed in tables
    """
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    cursor.execute(schema)

def update_clouds(df,dbase):
    """
    Update the shadow data from each station
    based on the data in datapath (the directory with the shadows)
    station contains the columns
    cloudiness
    description
    lat
    lon
    ID
    name
    the dbase contains columns
           stationID INTEGER,
           stationName TEXT,
           date TEXT,
           lat FLOAT,
           lon FLOAT,
           cloud INTEGER
    """
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    for k,ID in enumerate(df.ID):
        cloud=df.cloudiness.values[k]
        lat = df.lat.values[k]
        lon = df.lon.values[k]
        name = df.name.values[k]
        date = df.date.values[k]
        #find_station = f"SELECT * FROM clouds WHERE (stationID={ID});"
        find_station = f"SELECT * FROM clouds WHERE (stationID={ID} AND date={date});"
        entry = cursor.execute(find_station)
        if len(cursor.fetchall()) == 0:
            #print(f"Inserting {ID} for {date}")
            insert_row = ",".join([str(ID),"'"+name+"'",str(date),str(lat),str(lon),str(cloud)])
            com = '''INSERT OR REPLACE INTO clouds (stationID, stationName,date,lat, lon,cloud) VALUES ('''+insert_row+") "
            #com = f"INSERT OR IGNORE INTO clouds (stationID,stationName,lat,lon,cloud) VALUES ({ID},{name},{lat},{lon},{cloud});"
            cursor.execute(com)
        else:
            print(f"entry for {ID} already in shadows ")
        conn.commit()
    conn.close()


if __name__ == "__main__":
    if not os.path.isfile(DBASE):
        create_database(DBASE,create_clouds)
