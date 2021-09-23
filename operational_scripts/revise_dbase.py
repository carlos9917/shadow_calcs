#Not for operational purposes, just a quick script to check data!
import sqlite3
import pandas as pd
con=sqlite3.connect("shadows_data.db")
cursor=con.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables in file: %s"%cursor.fetchall())
sql_command = "SELECT * FROM STATIONS"
data_stations=pd.read_sql(sql_command, con)
print("Total number of stations: %d"%(data_stations.shape[0]+1))
print(data_stations.tail)
sql_command = "SELECT * FROM SHADOWS"
data_shadows=pd.read_sql(sql_command, con)
print(data_shadows.tail)
print("Current length of SHADOWS table : %d"%(data_shadows.shape[0]+1))
print(data_stations[data_stations.station_id==1804])
