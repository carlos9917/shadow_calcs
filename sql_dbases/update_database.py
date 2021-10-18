if __name__== '__main__':
    import shadows_database as sd
    import pandas as pd
    DBASES=["shadows_road_stretches.db","noshadows_daily_updates.db"]
    dbase_types=["road_stretch","noshadows"]

    COORDS=["/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/station_data_20211002.csv",
    "/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/station_noshadow_20211008.csv"]
    DATAPATHS = ["/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/lh_500_0.4_11.25_00",
    "/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/lh_500_0.4_11.25_noshadows_20210924"]
    for k,dbase_type in enumerate(dbase_types):
        if dbase_type=="road_stretch":
            #This one saves the old data, in which I named
            #stations with county and road, which are both zero
            mycols = ["station","name","lon","lat"]
            coords = pd.read_csv(COORDS[k],header=None)
            coords.columns = mycols
            sd.update_roadstations(DBASES[k],coords,DATAPATHS[k],"road_stretch") #st list
            sd.update_shadows(DBASES[k],DATAPATHS[k],"road_stretch") #shadows database
        if dbase_type=="noshadows":
            #For the new data I am pulling daily
            mycols = ["station","name","sensor1","sensor2","sensor3","lon","lat"]
            coords = pd.read_csv(COORDS[k],header=None)
            coords.columns = mycols
            sd.update_roadstations(DBASES[k],coords,DATAPATHS[k],"noshadows") #st list
            sd.update_settings(DBASES[k],DATAPATHS[k]) #settings
            sd.update_shadows(DBASES[k],DATAPATHS[k],"noshadows") #shadows database
