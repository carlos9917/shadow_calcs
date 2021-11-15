#Check the json dbase to see if station is there
import json
DBASE="./data_noshadows.json"

def search_station(station,sensor):
    with open(DBASE,"r") as f:
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

    args = parser.parse_args()
    station=args.station
    sensor=args.sensor
    out=search_station(station,sensor)
    print(out)
