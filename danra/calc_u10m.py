#just to produce the magnitude of u,v at 10 m
import os
import sys
import pandas as pd
import numpy as np

dir_path="15_dec_2019"
from pathlib import Path
for u_file in Path(dir_path).glob('*_u10_wind_*.csv'):
    if not "gust" in str(u_file):
        v_file = str(u_file).replace("u10_wind","v10_wind")
        #print(v_file)
        if os.path.isfile(v_file):
            print(f"Using {u_file} and {v_file}")
            df_u = pd.read_csv(u_file)
            df_v = pd.read_csv(v_file)
            dates = df_u["date"].to_list()
            u = df_u["value"].to_list()
            v = df_v["value"].to_list()
            u10 = []
            for k,u_k in enumerate(u):
                u10.append(np.sqrt(u_k*u_k + v[k]*v[k]))
            df = pd.DataFrame({"date":dates,
                                "value":u10})
            ofile=v_file.replace("v10_wind_10","U10m")
            print(f"Writing to {ofile}")
            df.to_csv(ofile,index=False)
