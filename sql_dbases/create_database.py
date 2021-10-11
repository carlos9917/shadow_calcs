if __name__== '__main__':
    DBASE="shadows_road_stretches.db"
    import create_database as cdbase
    tables = cdbase.schema()
    cdbase.create_database(DBASE,tables)
