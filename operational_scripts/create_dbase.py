#Create database with STATION and SHADOW tables

import sqlite3
import os
from datetime import datetime
import sys
import pandas as pd
from pandas import DataFrame

def new_db(dfile='shadows_data.db'):
    conn = sqlite3.connect(dfile)
    c = conn.cursor() 
    # Create table - STATIONS
    c.execute('''CREATE TABLE STATIONS
             ([generated_id] INTEGER PRIMARY KEY,[station_id] integer,[station_name] text, [lon] float, [lat] float, [Date] date)''')

    # Create table - SHADOWS
    c.execute('''CREATE TABLE SHADOWS
             ([generated_id] INTEGER PRIMARY KEY,[station_id] integer, [station_name] text, [resolution] float, [maxdistance] float, [horizonstep] float, [azimuth] float, [horizon_height] float, [Date] date)''')
        
    # Create table - DAILY_STATUS
    c.execute('''CREATE TABLE DAILY_STATUS
             ([station_id] integer, [station_name] text, [Date] date)''')
                 
    conn.commit()

# Note that the syntax to create new tables should only be used once in the code (unless you dropped the table/s at the end of the code). 
# The [generated_id] column is used to set an auto-increment ID for each record
# When creating a new table, you can add both the field names as well as the field formats (e.g., Text)
def update_db(shadow_dir,station_list,dfile='shadows_data.db'):
    '''
     Update both tables: SHADOWS and STATIONS
    '''

    conn = sqlite3.connect(dfile)
    c = conn.cursor()
    today=datetime.strftime(datetime.now(),"%Y/%m/%d")
    #header :station_id,station_name,lon,lat
    new_stations = pd.read_csv(station_list,header=None)
    new_stations.columns=['station_id','station_name','lon','lat']
    new_stations["Date"]=[today]*new_stations.shape[0]
    sql_com="SELECT * FROM STATIONS"
    current_stations=pd.read_sql(sql_com, conn)
    for station in current_stations.station_id.values:
        new_stations.drop(new_stations.index[new_stations['station_id'] == station], inplace = True)
    if not new_stations.empty:
        #if it found something new, update sql data base
        print("Updating STATIONS table")
        new_stations.to_sql('STATIONS', conn, if_exists='append', index = False)
    else:
        print("No new stations added to STATIONS table")
        return
    #read the database again if it was updated
    current_stations=pd.read_sql(sql_com, conn)
    sql_com="SELECT * FROM SHADOWS"
    shadow_old=pd.read_sql(sql_com, conn)
    #extract the info from the ifile
    from os.path import normpath, basename
    dir_info=basename(normpath(shadow_dir))
    #extract data from the name of directory
    maxdist,res,horstep,dummy=dir_info.replace("lh_","").split("_")
    stations=[]
    print("Checking for new data for SHADOWS table")
    for ifile in sorted(os.listdir(shadow_dir)):
        if ifile.startswith("lh_"):#will probably find shadows.log here
            station=int(ifile.replace("lh_","").split("_")[1])
            get_station=current_stations[current_stations['station_id']==station]
            if get_station.empty:
                print("Station %d not yet in STATIONS table"%station)
            else:
                print("Getting SHADOWS for station %d"%station)
                print("Reading shadows from %s"%os.path.join(shadow_dir,ifile))
                read_shadows=pd.read_csv(os.path.join(shadow_dir,ifile),index_col=False)
                size=read_shadows.shape[0]
                az=read_shadows.azimuth.to_list()
                hor=read_shadows.horizon_height.to_list()
                lon=get_station.lon.values[0]
                lat=get_station.lat.values[0]
                station_name=get_station.station_name.values[0]
                shadow_new=pd.DataFrame({"station_id":[station]*size,
                                         "station_name":[station_name]*size,
                                         "resolution":[res]*size,
                                         "maxdistance":[maxdist]*size,
                                         "horizonstep":[horstep]*size,
                                         "azimuth":az,
                                         "horizon_height":hor,
                                         "Date":[today]*size}
                                          )
                if shadow_old.empty:
                    shadow_new.to_sql('SHADOWS', conn, if_exists='append', index = False)
                else:
                    #drop from the new data any stations already in old data
                    for station in shadow_old.station_id.values:
                        shadow_new.drop(shadow_new.index[shadow_new['station_id'] == station], inplace = True)
                    if not shadow_new.empty:
                        shadow_new.to_sql('SHADOWS', conn, if_exists='append', index = False)
                    else:
                        print("No new data added to the SHADOWS table")
    print("database updated")
    c.execute('''
    INSERT INTO DAILY_STATUS (station_id,station_name,Date) 
    SELECT DISTINCT clt.station_id, ctr.station_name, clt.Date
    FROM STATIONS clt
    LEFT JOIN SHADOWS ctr ON clt.station_id = ctr.station_id
          ''')

    c.execute('''
    SELECT DISTINCT *
    FROM DAILY_STATUS
    WHERE Date = (SELECT max(Date) FROM DAILY_STATUS)
          ''')
    df = DataFrame(c.fetchall(), columns=['station_id','station_name','Date'])
    print("New data")
    print(df)

def clean_db(dfile='shadows_data.db'):
    '''
    Compare SHADOWS and STATIONS database and
    delete rows if the station_id does not match
    '''
    conn = sqlite3.connect(dfile)
    sql_com="SELECT * FROM STATIONS"
    current_stations=pd.read_sql(sql_com, conn)
    sql_com="SELECT * FROM SHADOWS"
    current_shadows=pd.read_sql(sql_com, conn)
    drop_rows=[]
    print("Current size of station data %d"%current_stations.shape[0])
    for k,station in enumerate(current_stations.station_id.values):
        check_shadows=current_shadows[current_shadows['station_id'] == station]
        if check_shadows.empty:
            print("Will remove station %d from STATIONS"%station)
            drop_rows.append(k)
        #else:
        #    print("Station %d ok"%station)
    if len(drop_rows) > 0:        
        print("Dropping stations")
        current_stations.drop(drop_rows, inplace = True)
        current_stations.to_sql('STATIONS', conn, if_exists='replace', index = False)
if __name__=='__main__':
    '''
    NOTE:
    station_list: the one with lat lon info
    '''
    station_list=sys.argv[1]
    shadow_dir=sys.argv[2]
    dfile="shadows_data.db"
    if not os.path.isfile(dfile):
       print("%s does not exist. Creating a new empty database first %s"%(dfile,dfile))
       new_db()
       print("Now attempting to update database %s"%dfile)
       update_db(shadow_dir=shadow_dir, station_list=station_list)
    else:
       print("%s found"%(dfile))
       #clean it first 
       clean_db()
       print("Attempting to update database %s"%dfile)
       update_db(shadow_dir=shadow_dir, station_list=station_list)
