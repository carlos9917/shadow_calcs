"""

Convert standard angles measures counterclockwise
from +X axis to compass direction


The angles produced by the r.horizon utility in Grass
follow this convention

According to the function's documentation
https://grass.osgeo.org/grass78/manuals/r.horizon.html

The directions are given as azimuthal angles (in degrees), with the angle starting with 0 towards East and moving counterclockwise (North is 90, etc.). The calculation takes into account the actual projection, so the angles are corrected for direction distortions imposed by it. The directions are thus aligned to those of the geographic projection and not the coordinate system given by the rows and columns of the raster map. This correction implies that the resulting cardinal directions represent true orientation towards the East, North, West and South. The only exception of this feature is LOCATION with x,y coordinate system, where this correction is not applied.

Using this function to convert the angles to cardinal directions
North is 0 degrees, East is 90 degrees, with angles measured clockwise
"""
import numpy as np

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

if __name__=="__main__":

    import argparse
    from argparse import RawTextHelpFormatter

    parser = argparse.ArgumentParser(description='''
             Convert angles to cardinal directions following
             the meteorological convention
             Example usage: python3 convertToCardinal.py -dir angle''', formatter_class=RawTextHelpFormatter)

    parser.add_argument('-dir',
           help='The angle I want to convert',
           type=float,
           default=None,
           required=True)

    args = parser.parse_args()
    if args.dir != None:
        angle = args.dir
        degs = standardToCompass(angle)
        print(degs)
