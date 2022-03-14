if __name__== '__main__':
    """
    Call this script to update both databases
    Define file names in DBASES

    COORDS are the list of lat lon coordinates for the stations,
    which are needed to store the data.

    DATAPATHS are the paths of the printouts of the shadows for the   
    stations
    """
    import argparse
    from argparse import RawTextHelpFormatter

    parser = argparse.ArgumentParser(description='''
             Example usage: python3 -coords list1,list2 -shadows  dir1,dir2 -dbases dbase1,dbase2''', 

                  formatter_class=RawTextHelpFormatter)
    parser.add_argument('-coords',
           help='The list of coordinates. If several, separate by commas',
           type=str,
           default=None,
           required=True)   

    parser.add_argument('-shadows',
           help='The list of directories with data. If several, separate by commas',
           type=str,
           default=None,
           required=True) 

    parser.add_argument('-dbases',
           help='The list of database names. If several, separate by commas',
           type=str,
           default=None,
           required=True)   

    parser.add_argument('-dbase_types',
           help='The types of data to process. If several, separate by commas',
           type=str,
           default=None,
           required=True)

    import shadows_database as sd
    import pandas as pd

    args = parser.parse_args()

    coords = args.coords
    dbases = args.dbases
    shadows = args.shadows
    dtypes = args.dbase_types #["road_stretch","noshadows"]
    
    if "," in  coords:
        COORDS= coords.split(",") #["shadows_road_stretches.db","noshadows_daily_updates.db"]
    else:
        COORDS = [coords]

    if "," in dbases:
        DBASES = dbases.split(",")
    else:
        DBASES = [dbases]

    if "," in shadows:
        DATAPATHS = shadows.split(",")
    else:
        DATAPATHS = [shadows]

    if "," in dtypes:
        dbase_types = dtypes.split(",")
    else:
        dbase_types = [dtypes]


    #dbase_types=["road_stretch","noshadows"]

    #COORDS=["/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/station_data_20211002.csv", "/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/station_noshadow_20211008.csv"]
    #DATAPATHS = ["/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/lh_500_0.4_11.25_00", "/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/lh_500_0.4_11.25_noshadows_20210924"]
    for k,dbase_type in enumerate(dbase_types):
        if dbase_type=="road_stretch":
            #This one saves the old data, in which I named
            #stations with county and road, which are both zero
            mycols = ["station","name","lon","lat"]
            coords = pd.read_csv(COORDS[k],header=None)
            print(f"Road stretch {COORDS[k]}")
            coords.columns = mycols
            #Update each table: station list, settings and shadows
            sd.update_roadstations(DBASES[k],coords,DATAPATHS[k],"road_stretch") #st list
            sd.update_settings(DBASES[k],DATAPATHS[k]) #settings
            sd.update_shadows(DBASES[k],DATAPATHS[k],"road_stretch") #shadows database
        if dbase_type=="noshadows":
            print("No shadows")
            #For the new data I am pulling daily
            mycols = ["station","name","sensor1","sensor2","sensor3","lon","lat"]
            coords = pd.read_csv(COORDS[k],header=None)
            coords.columns = mycols
            sd.update_roadstations(DBASES[k],coords,DATAPATHS[k],"noshadows") #st list
            sd.update_settings(DBASES[k],DATAPATHS[k]) #settings
            sd.update_shadows(DBASES[k],DATAPATHS[k],"noshadows") #shadows database
