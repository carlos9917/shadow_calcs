"""
Create the databases for the road stretches and the new stations
"""

if __name__== '__main__':
    import os
    dbases=["shadows_road_stretches.db",
            "noshadows_daily_updates.db"]
    import shadows_database as sd
    for dbase in dbases:
        if not os.path.isfile(dbase):
            tables = sd.schema()
            sd.create_database(dbase,tables)
