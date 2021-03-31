#Read the data collected by get_data.sh, add to sql file to keep track of stations already processed
import sqlite3
import pandas as pd
import sys
import os

def create_table(sql_file,table_name):
    """
    create an empty sql table
    """
    create_table_sql   = """CREATE TABLE IF NOT EXISTS """+table_name+"""
                              (ID INT DEFAULT NULL,
                               STATION INT DEFAULT NULL,
                               NAME TEXT DEFAULT NULL,
                               LON FLOAT DEFAULT NULL,
                               LAT FLOAT DEFAULT NULL,
                               PRIMARY KEY (ID, STATION));"""
    conn=sqlite3.connect(sql_file)
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def update_table(df_csv,sql_file,table_name):
    #Read the old database:
    conn = sqlite3.connect(sql_file)
    sql_command = "SELECT * FROM "+table_name
    old_df = pd.read_sql(sql_command, conn)
    #If file is not empty merge data
    if not old_df.empty:
        print(f"Updating table {table_name}")
        merge_data=pd.concat([old_df,df],sort=False)
        merge_data.drop_duplicates(keep="first",subset=["STATION","NAME","DAY"],inplace=True)
        #merge_data.drop_duplicates(subset='TIMESTAMP', keep='first',inplace=True)
        #(Pdb) check.drop_duplicates(keep="first",subset="TIMESTAMP").shape
        merge_data.to_sql(table_name,conn, if_exists="replace", index=False)
    #If file is empty then simple write data
    else:
        df.to_sql(table_name,conn, if_exists="append", index=False)



def create_dbase_stations(ifile,sql_file="station_list_gimli.db"):
    data.columns=['station','station_name','lon','lat']
    con = sqlite3.connect(sql_file)
    data.to_sql('station_list',con,if_exists="append", index=False)
    con.close()

def update_dbase_stations(ifile):
    sql_file="station_list.sqlite"
    conn=sqlite3.connect(sql_file)
    sql_command = "SELECT * FROM station_list"
    data_old=pd.read_sql(sql_command, conn)
    data_new=pd.read_csv(ifile,header=None,index_col=False)
    data_new.columns=['station','station_name','lon','lat']
    data_new.to_sql('station_list',conn,if_exists="replace", index=False)

if __name__=="__main__":
    sql_file = "gimli_stations.db"
    table_name = "gimli_stations"
    if len(sys.argv) == 1:
        print("Please provide name of the csv file")
        sys.exit()
    else:
        ifile=sys.argv[1]
        if not os.path.isfile(sql_file):
            print(f"Creating database {sql_file}")
            create_table(sql_file,table_name)
        else:
            data=pd.read_csv(ifile,header=None,index_col=False)
            print("Updating database")
            update_dbase_stations(ifile)
