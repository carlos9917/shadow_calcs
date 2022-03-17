# Maybe do this later using a heatmap.

cloud_cover = {1:"cloud free land",
               2: "cloud free sea",
               3: "snow over land",
               4: "sea ice",
               5: "very low clouds",
               6: "low clouds",
               7: "mid-level clouds",
               8: "high opaque clouds",
               9: "very high opaque clouds",
               10: "fractional clouds",
               11: "high semitransparent thin clouds",
               12: "high semitransparent moderately thick clouds",
               13: "high semitransparent thick clouds",
               14: "high semitransparent above low or medium clouds",
               15: "high semitransparent above snow/ice",
               16: "high semitransparent thin cirrus",
               17: "high semitransparent thick cirrus",
               18: "high semitransparent cirrus above low or medium level clouds",
               19: "fractional clouds",
               20: "undefined"}


import pandas as pd
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
from datetime import datetime
import matplotlib.dates as md

cloud_type=16
ifile="data_202202_aero.csv"
data = pd.read_csv(ifile)
data.astype({'cloudiness': 'int32'}).dtypes
df=data[data["cloudiness"] == cloud_type]
if df.empty:
    print(f"No data found for {cloud_type}")
    sys.exit(1)
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_ylabel("cloudiness")
#dates=[datetime.strptime(str(date),"%Y%m%d%H%M%S") for date in df["date"]]
#for k,date in enumerate(df["date"]):
#    this_date=[datetime.strptime(str(date),"%Y%m%d%H%M%S")]
#    print(f"{k} {this_date}")
dates=[dt for dt in [datetime.strptime(str(date),"%Y%m%d%H%M%S") for date in df.date.to_list()] ]
clouds=df.cloudiness.to_list()
plt.stem(dates,clouds)

xfmt = md.DateFormatter('%Y-%m-%d %H')
ax.xaxis.set_major_formatter(xfmt)
from matplotlib.ticker import MaxNLocator
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
fig.autofmt_xdate()
plt.xticks(rotation=40)
#plt.show()

fig.suptitle("Cloudiness = "+str(cloud_type)+" ("+cloud_cover[cloud_type]+" )")
plt.savefig("cloudy_"+str(cloud_type).zfill(2)+".png")



#Filter the 
