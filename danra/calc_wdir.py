#calculate the wind direction at 10 m
# loops over all files in dir_path
import os
import sys
import pandas as pd
import numpy as np

def calc_wdir10(dir_path):
    from pathlib import Path
    for u_file in Path(dir_path).glob('*_u10_wind_*.csv'):
        if not "gust" in str(u_file):
            v_file = str(u_file).replace("u10_wind","v10_wind")
            #print(v_file)
            if os.path.isfile(v_file):
                print(f"Using {u_file} and {v_file} to calculate WDIR10")
                df_u = pd.read_csv(u_file)
                df_v = pd.read_csv(v_file)
                dates = df_u["date"].to_list()
                u = df_u["value"].to_list()
                v = df_v["value"].to_list()
                wdir = []
                for k,u_k in enumerate(u):
                    #note that when using np.arctan2 the first element is the "y", the second the "x"
                    #some other libs might have it reversed
                    #method 1. Gives same result as the method from ecmwf below
                    #wind_dir_trig_to_met= (270-np.rad2deg(np.arctan2(v[k],u_k)))%360

                    #method 2: https://confluence.ecmwf.int/pages/viewpage.action?pageId=133262398
                    wind_dir_trig_to_met = np.mod (180 + 180*np.arctan2(v[k],u_k)/np.pi,360)

                    #method 3, from youtube video
                    wind_dir_trig_to_met = np.mod(270 - 180*np.arctan2(u_k,v[k])/np.pi,360)

                    wdir.append(wind_dir_trig_to_met)
                df = pd.DataFrame({"date":dates,
                                    "value":wdir})
                ddir,fname = os.path.split(v_file)
                date_file = fname.split("_")[-1].replace(".csv","") #"Bellahoej_u10_wind_10_2015112700.csv"
                station = fname.split("_")[0]
                ofile=os.path.join(dir_path,"_".join([station,"WDIR10m",date_file])+".csv")
                print(f"Writing to {ofile}")
                df.to_csv(ofile,index=False)

if __name__=="__main__":
    #test the calculation
    calc_wdir10("./test_wdir")
