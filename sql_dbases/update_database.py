if __name__== '__main__':
    import shadows_database as sd
    import pandas as pd
    DBASE="shadows_road_stretches.db"
    dbase_type="road_stretch" #"noshadows"

    COORDS="/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/station_data_20211002.csv"
    datapath = "/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/lh_500_0.4_11.25_00"

    if dbase_type=="road_stretch":
        mycols = ["station","name","lon","lat"]
        coords = pd.read_csv(COORDS,header=None)
        coords.columns = mycols
        sd.update_roadstations(DBASE,coords,datapath,"road_stretch") #st list
        sd.update_settings(DBASE,datapath) #settings
        sd.update_shadows(DBASE,datapath,"road_stretch") #shadows database
    if dbase_type=="noshadows":
        mycols = ["station","name","sensor1","sensor2","sensor3","lon","lat"]
        coords = pd.read_csv(COORDS,columns=mycols)
