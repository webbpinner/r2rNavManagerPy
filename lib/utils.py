#!/usr/bin/env python3
'''
        FILE:  utils.py
 DESCRIPTION:  Contains various utility functions used by the r2rNavManagerPy
               programs.

        BUGS:
       NOTES:
      AUTHOR:  Webb Pinner
     COMPANY:  OceanDataTools
     VERSION:  0.2
     CREATED:  2021-04-15
    REVISION:  2021-05-05

LICENSE INFO: This code is licensed under MIT license (see LICENSE.txt for details)
              Copyright (C) OceanDataTools 2021
'''

import os
import glob
import math
import logging
import pandas as pd

################################################################################
def build_file_list(path, sort=True, unique=True):
    """
    Build a list of files based on the path.  If the path is a file the function
    returns a list containing the file.  If the path is a directory the function
    returns a list of files in the directory.  If the path is a list of files/
    directories the function returns a list of all the files and the files in
    the directories

    By default the function will sort the file_list and only return unique
    filenames
    """

    file_list = []

    if isinstance(path, list):
        for item in path:
            file_list += build_file_list(item)

    elif os.path.isfile(path):
        file_list.append(path)

    elif os.path.isdir(path):
        for i in glob.glob(os.path.join(path, "*")):
            if os.path.isfile(i):
                file_list.append(i)

            elif os.path.isdir(i):
                file_list.append(build_file_list(i))

    # eliminate duplicates
    if unique:
        file_list = list(dict.fromkeys(file_list))

    # sort list
    if sort:
        file_list.sort()

    return file_list


################################################################################
def is_valid_nav_format(nav_format):
    """
    Returns true if specified nav_format is valid, else returns false
    """

    return nav_format in get_nav_formats()

################################################################################
def get_nav_formats():
    """
    Returns list of valid nav formats
    """

    valid_nav_formats = ['nav01','nav02','nav03','nav33']

    return valid_nav_formats


def calculate_bearing(point_b, point_a):
    """
    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `point_a: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `point_b: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    if not isinstance(point_a, tuple) or not isinstance(point_b, tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(point_a[0])
    lat2 = math.radians(point_b[0])

    diff_long = math.radians(point_b[1] - point_a[1])

    x_pos = math.sin(diff_long) * math.cos(lat2)
    y_pos = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diff_long))

    initial_bearing = math.atan2(x_pos, y_pos)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing


def read_r2rnavfile(file, file_format='csv'):
    """
    Read the specifed r2rnav formatted file.  Returns a dataframe if successful
    Return None if the file could not be read.
    """

    if file_format == 'hdf':
        try:
            data = pd.read_hdf(file)
            return data
        except IOError:
            logging.error("Error opening file r2rnav file: %s", file)
    elif file_format == "csv":
        try:
            data = pd.read_csv(file)
            data['iso_time'] = pd.to_datetime(data['iso_time'])
            data['sensor_time'] = pd.to_datetime(data['sensor_time'])
            data['deltaT'] = pd.to_timedelta(data['deltaT'])
            data['sensor_deltaT'] = pd.to_timedelta(data['sensor_deltaT'])
            return data
        except IOError:
            logging.error("Error opening file r2rnav file: %s", file)
        except Exception as err:
            logging.error("Error parsing csv file")
            logging.error(str(err))

    return None


def hemisphere_correction(coordinate, hemisphere):
    if hemisphere in ('W', "S"):
        return coordinate * -1.0

    return coordinate


def verify_checksum(sentence):
    cksum = sentence[len(sentence) - 2:]
    chksumdata = re.sub("(\n|\r\n)","", sentence[sentence.find("$")+1:sentence.find("*")])

    csum = 0

    for char in chksumdata:
        # XOR'ing value of csum against the next char in line
        # and storing the new XOR value in csum
        csum ^= ord(char)

    return 1 if hex(csum) == hex(int(cksum, 16)) else 0
