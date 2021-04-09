'''
Search database for a given station and extract the shadows
to an ASCII file
'''
import sqlite3
import sys
import os
import pandas as pd
import numpy as np

def main(st,db):
    write_these = ["azimuth","horizon_height","horizonstep","resolution","maxdistance"]
    con=sqlite3.connect("shadows_data.db")
    cursor=con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    all_tables = cursor.fetchall()
    print(f"Tables in file: {all_tables}")
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
                        required=True)

    parser.add_argument('-db',metavar='Sqlite file with data',
                        type=str,
                        default="./shadows_data.db",
                        required=False)



    args = parser.parse_args()
    station=args.st
    dfile=args.db

    if not os.path.isfile(dfile):
       print(f"{dfile} database does not exist!")
       sys.exit(1)
    main(station,dfile)

