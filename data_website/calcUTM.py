#calculate UTM from lat lon
from pyproj import Proj
import pyproj
import sys
import pandas as pd
from collections import OrderedDict
import numpy as np
import os

def read_data(ifile):
    #Read the data from a file
    #5160,"Gjørup",9.36827374,56.65630341
    data=pd.read_csv(ifile,sep=",",header=None)
    data.columns=['roadnr','loc','lon','lat']
    return data

def latlon2utm(lat,lon):
    #this used to work in py36
    #etrs89=Proj("+init=EPSG:4258") 
    #UTM32N=pyproj.Proj("+init=EPSG:25832") 
    #old style:
    #east,north= pyproj.transform(etrs89,UTM32N,lon,lat)
    #print("{:.6f} {:.6f}".format(east,north))
    #modification for py38 version
    from pyproj import Transformer
    transformer=Transformer.from_crs(4258,25832,always_xy=True)
    for pt in transformer.itransform([(float(lon),float(lat))]): 
        res='{:.6f} {:.6f}'.format(*pt)
    east,north=res.split()
    return east,north

if __name__ == '__main__':

    if len(sys.argv) == 3:
        lat=sys.argv[1]
        lon=sys.argv[2]
        east,nort=latlon2utm(lat,lon)
        print(str(east)+" "+str(nort))
    elif len(sys.argv) == 2:
        try:
            ifile=sys.argv[1]
            print("Read file %s"%ifile)
        except:    
            print("No file!")
        data=read_data(ifile)
        dout=OrderedDict()
        dout['easting']=np.array([])
        dout['norting']=np.array([])
        dout['roadnr']=np.array([])
        dout['county']=np.array([])
        dout['roadsection']=np.array([])
        for k,lat in enumerate(data.lat.values):
            east,nort=latlon2utm(lat,data.lon.values[k])
            dout['easting'] = np.append(dout['easting'],east)
            dout['norting'] = np.append(dout['norting'],nort)
            dout['roadnr']=np.append(dout['roadnr'],str(data.roadnr.values[k]))
            dout['roadsection']=np.append(dout['roadsection'],'0')
            dout['county']    =np.append(dout['county'],'0')
        write_out=pd.DataFrame({'easting':dout['easting'],'norting':dout['norting'],'roadnr':dout['roadnr'],'roadsection':dout['roadsection'],'county':dout['county']})
        ofile=os.path.split(ifile)[-1].replace(".csv","_utm.csv")
        print("output file %s"%ofile)
        write_out.to_csv(ofile,sep='|',float_format='%.3f',index=False,header=False)
    else:
        print("Please provide either one of the these command line arguments")
        print("Option 1: python3 calcUTM.py lat lon")
        print("Option 2: python3 calcUTM.py filename")

