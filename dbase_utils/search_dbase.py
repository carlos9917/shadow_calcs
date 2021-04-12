'''
Search database for a given station and extract the shadows
to an ASCII file
Currently only tables SHADOWS and STATIONS have data

'''
import sqlite3
import sys
import os
import pandas as pd
import numpy as np
def print_dbase_summary(db,short=True):
    table_name="STATIONS"
    con=sqlite3.connect("shadows_data.db")
    cursor=con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    all_tables = cursor.fetchall()
    #print(f"Tables in file: {all_tables}")
    sql_command = "SELECT * FROM "+table_name
    data_stations=pd.read_sql(sql_command, con)
    if not data_stations.empty:
        ns = data_stations.shape[0]+1
        if short:
            print("SHORT SUMMARY OF AVAILABLE STATIONS")
            print(f"Total number of stations: {ns}")
            print("First 10")
            print(data_stations[["station_id","station_name","lon","lat"]].head())
            print("Last 10")
            print(data_stations[["station_id","station_name","lon","lat"]].tail())
        else:
            print(f"Total number of stations: {ns}")
            print("STATIONS AVAILABLE")
            print(data_stations[["station_id","station_name","lon","lat"]].to_markdown(tablefmt="grid",index=False))
    else:
        print(f"WARNING: {db} is empty!")

def extract_station(st,db):
    write_these = ["azimuth","horizon_height","horizonstep","resolution","maxdistance"]
    con=sqlite3.connect("shadows_data.db")
    cursor=con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    sql_command = "SELECT * FROM STATIONS"
    data_stations=pd.read_sql(sql_command, con)
    if not data_stations.empty:
        ns = data_stations.shape[0]+1
        print(f"Total number of stations: {ns}")
        #print(data_stations.tail)
        sql_command = "SELECT * FROM SHADOWS"
        data_shadows=pd.read_sql(sql_command, con)
        st_data = data_shadows[data_shadows["station_id"] == st]
        if not st_data.empty:
            azimuth = st_data["azimuth"].values
            hor =  st_data["horizon_height"].values
            step =  str(st_data["horizonstep"].values[0])
            res =  str(st_data["resolution"].values[0])
            dist = str(int(st_data["maxdistance"].values[0]))
            fname = "_".join([str(st),"shadow",dist,res,step])+".csv"
            #data = np.c_[azimuth,hor]
            #with open(fname,"w") as f:
            #    np.savetxt(f,data,fmt='%g %g')
            data = [st_data["azimuth"],st_data["horizon_height"]]
            headers=["azimuth","horizon_height"]
            df = pd.concat(data,axis=1,keys=headers)
            #df.astype('str').dtypes
            df.to_csv(fname,index=False)
            
            #print(f"{azimuth} {hor}")
        else:    
            print(f"{st} not found in {db}")
    else:
        print(f"WARNING: {db} is empty!")
        sys.exit(1)



if __name__=='__main__':
    '''
    NOTE:
    station_list: the one with lat lon info
    '''
    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description='''
            Fetch shadow data from a given station. 
            Example usage: python3 search_database.py -st 1001 -db shadows_data.db
                           ''',formatter_class=RawTextHelpFormatter)

    parser.add_argument('-st',metavar='station to fetch (integer)',
                        type=int,
                        default=None,
                        required=False)

    parser.add_argument('-db',metavar='Sqlite file with data',
                        type=str,
                        default="./shadows_data.db",
                        required=False)
    parser.add_argument('-sshort',action='store_true', help="Print short table summary") # false by default
    parser.add_argument('-slong',action='store_true', help="Print long table summary") # false by default



    args = parser.parse_args()
    station=args.st
    dfile=args.db

    if args.sshort:
        print_dbase_summary(dfile)
        sys.exit(0)
    elif args.slong:
        print_dbase_summary(dfile,short=False)
        sys.exit(0)

    if not os.path.isfile(dfile):
       print(f"{dfile} database does not exist!")
       sys.exit(1)
    if station is not None:
        extract_station(station,dfile)
    else:
        print("Station number not provided")

