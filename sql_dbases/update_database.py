if __name__== '__main__':
    import shadows_database as cdbase
    DBASE="shadows_road_stretches.db"
    datapath = "/media/cap/7fed51bd-a88e-4971-9656-d617655b6312/data/glatmodel_model/dirs_shadows/lh_500_0.4_11.25_00"
    cdbase.update_database(DBASE,datapath)
