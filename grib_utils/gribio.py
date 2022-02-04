import eccodes as ecc
from collections import OrderedDict
import eccodes as ecc
import numpy.ma as ma
from datetime import datetime
import os

class grib:
    """
    Class to read grib files. Using eccodes (must be at least 2.21)

    Parameters
    ----------
    gribfile : str
        Path to the grib file to be used

    indicatorOfParameter : int
        indicator of the parameter to be read (ie, 11 for t2m, etc)

    levelType : int
        type of level (100 for pressure levels, 105 for surface)
        I define a dictionary below, since the gribcodes are printed as strings. Not sure how to change that

    level : int
        The level I want to read

    timeRangeIndicator: int
        Indicator of time range. Usually set to 0

    """
    def __init__(self, gribfile:str, indicatorOfParameter:int, levelType:int, level:int, timeRangeIndicator:int, stationId: None) -> None:
        level_types = {100:"pl", 105:"sfc"} # not sure how write these as integer in grib messages
        self.engine='eccodes' #maybe add pygrib later as a backup
        self.gribfile = gribfile
        self.indicatorOfParameter = indicatorOfParameter
        self.level = level
        self.levelType = level_types[levelType]
        self.timeRangeIndicator = timeRangeIndicator
        self.stationId = stationId

    def get_data_fromidx(self,gid,latlonidx):
        """
        Get the data for lan and lon when I know the idx
        """
        data_nearest = ecc.codes_get_elements(gid,'values',latlonidx[0]["index"])[0]
        return data_nearest

    def get_data_nearest(self,lat,lon):
        """
        Loop through the data and check the nearest value to lat lon
        """
        data_found = []
        #f = open(self.gribfile)
        with open(self.gribfile) as f:
            while 1:
                gid = ecc.codes_grib_new_from_file(f)
                #idx = ecc.codes_index_new_from_file(f,['date', 'time', 'shortName', 'level', 'step'])
                if gid is None:
                    break
                latlonidx = ecc.codes_grib_find_nearest(gid,lat,lon)
                lat_found = latlonidx[0]["lat"]
                lon_found = latlonidx[0]["lon"]
                data_nearest = ecc.codes_get_elements(gid,'values',latlonidx[0]["index"])[0]
                data_found.append(data_nearest)
                #print(latlonidx)
                print(f"Requested: {lat},{lon}")
                print(f"Nearest coordinates: {lat_found},{lon_found}")
                print(f"Nearest data: {data_nearest}")
                #ecc.codes_release(gid)
        return data_found


    def check_codes(self) -> None:
        """
        Loop through all codes. This is just to do a quick check
        """
        f = open(self.gribfile)
        while 1:
            gid = ecc.codes_grib_new_from_file(f)
            if gid is None:
                break
            keys = ("indicatorOfParameter",'name', 'shortName', 'levelType','level','timeRangeIndicator')
            keys = ("indicatorOfParameter",'name', 'levelType','level','timeRangeIndicator')
            check_key =  ecc.codes_get(gid, "indicatorOfParameter")
            #print(check_key)
            for key in keys:
                #string format
                #print(f'(key, code): ({key},{ecc.codes_get(gid, key)})')
                print(f'{key} ----> {ecc.codes_get(gid, key)}')
                #int format
                #print(f'(key,code) {key},{ecc.codes_get(gid, key,ktype=int)}')


    def get_dims(self) -> tuple:
        """
        Get the grid dimensions
        """
        with open(self.gribfile) as f:
            while 1:
                gid = ecc.codes_grib_new_from_file(f)
                if gid is None:
                    break
                Nx = ecc.codes_get(gid, "Nx")
                Ny = ecc.codes_get(gid, "Ny")
                #print(f"Nx: {Nx}")
                #print(f"Ny: {Ny}")
        return Nx, Ny

    def get_data_location(self) -> OrderedDict:
        """
        Read the data for specific location and all times, return as 
        """
        pass

    def get_data(self) -> OrderedDict:
        """
        Read the data for all times, return  as an ordered dict

        The ordered dict contains:

        values: an ordered dict with the values for each time in an ordered dict
                The elements of the ordered dict are integers representing
                the lead times: 0,300,600,900, etc
        date: the current date in the file
        lats: numpy array with the latitudes  of the domain
        lons: numpy array with the longitudes of the domain
        fctstep: the forecast step
        grid: the type of grid (usually lambert)
        param: the name of the parameter (parameterName)

        """
        data = OrderedDict()
        data["values"] = OrderedDict()
        #print(self.gribfile)
        with ecc.GribFile(self.gribfile) as g:
            for msg in g:
                #print(msg['indicatorOfParameter'])
                print(f'Going through level {msg["level"]}')
                #print(msg['levelType'])
                if msg['indicatorOfParameter'] == self.indicatorOfParameter and msg['level'] == self.level and msg['levelType'] == self.levelType and msg["timeRangeIndicator"] == self.timeRangeIndicator:
                    print(">>>>>> Found the data <<<<<<< ")
                    latlonidx = ecc.codes_grib_find_nearest(msg.gid,55.995613,12.486561)
                    this_data = self.get_data_fromidx(msg.gid,latlonidx)
                    print(f"Check data for specifif lat and lon {this_data}")
                    nx,ny = self.get_dims()
                    #data[msg["time"]]=ma.masked_values(msg["values"].reshape((ny,nx)),msg['missingValue'])
                    date = msg['date']
                    hour = msg['hour']
                    fcstep = msg['step']
                    lons = msg['longitudes'].reshape((ny,nx))
                    lats = msg['latitudes'].reshape((ny,nx))
                    dt = datetime.strptime(str(date)+str(hour),"%Y%m%d%H")
                    data["values"][dt]=ma.masked_values(msg["values"].reshape((ny,nx)),msg['missingValue'])
                    #proj = ccrs.PlateCarree()
                    #data["validtime"] = dt
                    data["lons"] = lons
                    data["lats"] = lats
                    data["fcstep"] = fcstep
                    data["grid"] = msg["gridType"]
                    #'proj':proj,# should I include projection?
                    #data["param"] = msg["parameterName"]
                    #data = msg.get("values")
                    #print(msg.size())
                    data["indicatorofparameter"] = msg["indicatorOfParameter"]
                    data["level"] = msg["level"]
                    data["levelType"] = msg["levelType"]
        return data


    def get_mval(self):
        """
        returns the missing value
        """
        with ecc.GribFile(self.gribfile) as g:
            for msg in g:
                return msg.get("missingValue")


    def get_times(self) -> list:
        """
        returns all times in the file
        """
        times = []
        with ecc.GribFile(self.gribfile) as g:
            for msg in g:
                times.append(msg["time"])
        return times

if __name__== "__main__":


    indicatorOfParameter =171
    levelType=105
    level=0
    timeRangeIndicator=0
    files=os.listdir(".")
    findLat = 55.995613
    findLon = 12.486561
    stationId = "Test"
    gribfile="SAFNWC_MSG_CMa_area_FM3_202201310015"
    #print(files)
    g = grib(gribfile=gribfile,indicatorOfParameter=indicatorOfParameter,level=level,levelType=levelType,timeRangeIndicator=timeRangeIndicator,stationId=stationId)
