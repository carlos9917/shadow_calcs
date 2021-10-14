if __name__== '__main__':
    DBASE="shadows_road_stretches.db"
    import shadows_database as sd
    tables = sd.schema()
    sd.create_database(DBASE,tables)
