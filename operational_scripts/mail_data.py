"""
Look at the data generated (if any) and
email it in specified format

#station_number,sensor_number,shadow_1....shadow_32

Example:
1549,0,0,10,6,4,4,4,6,4,2,8,6,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,2,4,2,0,0,0
2038,0,6,6,4,4,2,2,2,0,2,6,13,15,19,21,22,22,22,22,17,15,11,6,0,0,0,2,2,4,4,6,6,6
2038,1,4,6,4,2,2,2,0,2,10,15,22,30,33,37,39,37,37,35,30,26,19,11,4,0,0,0,2,2,4,4,4,4
5016,0,8,13,15,15,13,15,11,8,2,6,10,11,11,8,8,8,8,11,19,19,6,8,8,6,0,10,11,10,8,11,11,19
5016,1,6,8,8,11,8,8,8,6,2,8,10,10,17,15,10,11,13,15,17,15,15,13,10,2,6,17,21,19,19,19,17,11
5242,0,6,8,2,6,17,13,11,6,2,8,10,8,8,8,6,41,48,52,52,53,52,17,8,8,6,2,4,8,13,11,4,4
5242,1,8,8,4,6,17,17,13,6,4,2,8,4,6,6,4,32,48,50,39,32,21,11,4,4,0,2,6,11,13,8,8,6
6110,0,0,0,0,0,0,0,0,4,4,4,6,6,6,11,11,17,15,15,15,11,2,0,0,0,0,0,0,0,0,0,0,0
6110,1,0,0,0,0,0,0,2,4,8,6,8,22,28,8,19,24,26,19,15,11,6,0,2,0,0,0,0,0,0,0,0,0

Direction is clock wise.
  0 North
 90 east
180 south
270 West
"""

import pandas as pd
import os
import numpy as np
import sys

def standardToCompass(angle):
    """
    Convert angle measured from +X axis counterclockwise
    to angle measured clockwise from +Y axis
    This only works for *wind directions*!
    """
    compass = 90 - angle
    if compass < 0:
        compass = compass + 360
    compass = compass + 180
    if compass >= 360:
        compass = compass - 360
    #Up to here the result is ok for wind fetch,
    # but I want just the angle
    compass = compass + 180    
    #reset to 0 if it goes above 360
    if compass >= 360:
        compass = compass - 360
    return compass

def reformat(datapath):
    stations = []
    for ifile in sorted(os.listdir(datapath)):
        if ifile.startswith("lh_"):#will probably find shadows.log here
            station = ifile.split("_")[1]
            sensor = ifile.split("_")[2]
            data = pd.read_csv(os.path.join(datapath,ifile))
            angles = data.azimuth.to_list()
            shadows = data.horizon_height.to_list()
            angles_rot=[]
            for angle in angles:
                convAngle = standardToCompass(angle)
                #print(f"converting angle {angle} to {convAngle}")
                angles_rot.append(convAngle)
            s = np.array(angles_rot)
            sort_index = np.argsort(s)
            shadows_order = [str(shadows[i]) for i in sort_index]
            angles_order = [angles_rot[i] for i in sort_index]
            print("Ordered angles and shadows")
            print_df = pd.DataFrame({"angle":angles,
                                     "shadow": shadows, 
                                     "angle_rotated": angles_rot,
                                     "angle_met": angles_order,
                                     "shadow_met": shadows_order})
            print(print_df.to_markdown())
            stations.append(",".join([station,sensor]+shadows_order))
            stations.append("\n")
    return stations     

def mail_data(stations,fout,user="cap"):
    import subprocess
    txt = "".join(stations)
    with open(fout,"w") as f:
        f.write(txt)
    cmd='mail -s "Shadows data" '+user+'@dmi.dk < '+ fout
    #print(cmd)
    try:
        out=subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
    except subprocess.CalledProcessError as err:
        print("Email failed with error %s"%err)


def save2json(input_filename,output_filename):
    """
    Save the station data in json format
    The input_filename is the one to be emailed

    """
    import json
    all_data=[]
    #open the old file if already there
    if os.path.isfile(output_filename):
        print("Data file already there. Checking contents")
        with open(output_filename,"r") as json_file:
            json_strings = json.load(json_file)
        for json_str in json_strings:
            read_json = json.loads(json_str)
            station = read_json["station"]
            sensor = read_json["sensor"]
            print(f"Station and sensor: {station} {sensor}")
            all_data.append(json_str)
    print(f"Currently read {len(all_data)}")
    with open(input_filename,"r") as f:
        lines=f.readlines()
        station_dict={}
        for line in lines:
            station_dict["station"] = line.split(",")[0]
            station_dict["sensor"] = line.split(",")[1]
            station_dict["data"] = data=",".join(line.rstrip().split(",")[2:])
            #convert dict to json
            y=json.dumps(station_dict)
            all_data.append(y)
    all_data=sorted(set(all_data)) #select only not repeated
    print("Strings to write")
    print(len(all_data))
    with open(output_filename,"w") as f:
        json.dump(all_data,f,indent=4)


if __name__=="__main__":
    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description='''
             Example usage: python3 mail_data.py -shadows ./lh_500_0.4_11.25_00 -message deliver_data.txt''', formatter_class=RawTextHelpFormatter)

    parser.add_argument('-shadows',
           help='The directory where the shadows are stored',
           type=str,
           default='./lh_500_0.4_11.25_00',
           required=False)

    parser.add_argument('-message',
           help='The name of the file with the message to email',
           type=str,
           default=None,
           required=True)

    parser.add_argument('-dbase',
           help='The name of file with the json data',
           type=str,
           default="./data_noshadows.json",
           required=True)

    args = parser.parse_args()

    datapath = args.shadows
    if not os.path.isdir(datapath):
        print(f"{datapath} does not exist!")
        sys.exit(1)
    file2email = args.message #"deliver_station_data.txt"
    file2json = args.dbase
    #Read data in output dir and reformat for email
    stations = reformat(datapath)
    #Currently not working from volta, so doing
    #the mail command after the data is pulled from hpcdev
    mail_data(stations,file2email)
    #Save the data to json file
    save2json(file2email,file2json)

