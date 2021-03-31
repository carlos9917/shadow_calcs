#read database and generate the old data 
import pandas as pd
import sqlite3
from collections import OrderedDict
import os
import subprocess
def extract_data(dfile='shadows_data.db'):
    con = sqlite3.connect(dfile)
    sql_com="SELECT * FROM STATIONS"
    station_data=pd.read_sql(sql_com, con)
    shadows=[];stations=[]
    sql_com="SELECT * FROM SHADOWS"
    shadow_data=pd.read_sql(sql_com, con)
    odir='lh_500_0.4_11.25_00'
    if not os.path.exists(odir):
        os.makedirs(odir)
    missing_data=OrderedDict()
    drop_data=[]
    for var in  ['station_id', 'station_name', 'lon', 'lat']:
        missing_data[var]=[]
    for k,station in enumerate(station_data.station_id):
        sel_data=shadow_data[shadow_data.station_id==station]
        if sel_data.empty: 
            print("Station %d missing in SHADOWS"%station)
            missing_data['station_id'].append(station)
            missing_data['station_name'].append(station_data.station_name.values[k])
            missing_data['lon'].append(station_data.lon.values[k])
            missing_data['lat'].append(station_data.lat.values[k])
            #delete this row from the database
            ix=station_data[station_data.station_id==station].index[0]
            drop_data.append(station_data.index[ix])
        else:
            az=sel_data.azimuth.to_list()
            hor=sel_data.horizon_height.to_list()
            ofile='_'.join(['lh','0',str(station),'0'])+'.txt'
            lh_data=pd.DataFrame({'azimuth':az,'horizon_height':hor})
            lh_data.to_csv(os.path.join(odir,ofile),index=False)
            del lh_data
    if len(missing_data) > 0: 
        print("Ammending the database",dfile)
        cmd="cp "+dfile+ " "+dfile+".save"
        out=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
        import csv
        write_missing=pd.DataFrame(data=missing_data)
        write_missing.station_name = write_missing.station_name.astype(str)

        write_missing.to_csv(os.path.join(odir,"missing_stations"),index=False,header=None,quotechar='"',quoting=csv.QUOTE_NONNUMERIC)
        station_data.drop(drop_data,inplace=True)
        station_data.to_sql('STATIONS', con, if_exists='replace', index = False)
    else:
        print("Found all stations in data")
if __name__=='__main__':
    extract_data()
