#Check the json dbase to see if station is there
import json
DBASE="./data_noshadows.json" #default

def search_station(station,sensor,dbase):
    with open(dbase,"r") as f:
        data = json.load(f)
    output=f"{station},{sensor} not found!"
    for item in data:
        element = json.loads(item)
        if element["station"] == station and element["sensor"] == sensor:
            shadows = element["data"]
            output=f"{station},{sensor},{shadows}"
    return output
                

if __name__=="__main__":
    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description='''
            Example usage: python3 check_json.py -station 2038 -sensor 0''',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-station',help='station to search',
                        type=str,
                        default=None,
                        required=True)

    parser.add_argument('-sensor',help='sensor to search',
                        type=str,
                        default=None,
                        required=True)

    parser.add_argument('-jfile',help='json file',
                        type=str,
                        default=DBASE,
                        required=False)

    args = parser.parse_args()
    station=args.station
    sensor=args.sensor
    jfile=args.jfile
    out=search_station(station,sensor,jfile)
    print(out)
