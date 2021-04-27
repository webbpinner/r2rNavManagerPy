#!/usr/bin/env python3
# ----------------------------------------------------------------------------------- #
#
#         FILE:  nav03_parser.py
#
#  DESCRIPTION:  Nav03 parser class for GLL data prefixed with the SCS formatted
#                timestamp (mm/dd/YYYY,HH:MM:SS.sss) and comma (,).  Data may contain
#                random NMEA0183 GGA, VTG and ZDA sentences.    None of the sentences
#                contain trailing checksums.
#
#         BUGS:
#        NOTES:
#       AUTHOR:  Webb Pinner
#      COMPANY:  OceanDataTools
#      VERSION:  0.1
#      CREATED:  2021-04-27
#     REVISION:  
#
# LICENSE INFO: This code is licensed under MIT license (see LICENSE.txt for details)
#               Copyright (C) OceanDataTools 2021
#
# ----------------------------------------------------------------------------------- #
import os
import re
import csv
import sys
import logging
import pandas as pd
from datetime import datetime, timedelta
from geopy import Point
from geopy.distance import distance, great_circle

from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

from lib.nav_manager import NavParser
from lib.utils import calculate_bearing

description = "Nav parser for GLL data prefixed with the SCS formatted timestamp (mm/dd/YYYY,HH:MM:SS.sss) and comma (,).  Data may contain random NMEA0183 GGA, VTG and ZDA sentences.  None of the sentences contain trailing checksums."

example_data = """
10/05/2010,13:05:48.703,$GPVTG,55,T,56,M,8.8,N,16.3,K
10/05/2010,13:05:58.703,$GPGGA,130517,4651.698,N,09153.945,W,1,8,0.3,201,M,-32,M
10/05/2010,13:06:08.750,$GPVTG,55,T,56,M,8.8,N,16.4,K
10/05/2010,13:06:18.703,$GPVTG,56,T,57,M,8.8,N,16.3,K
10/05/2010,13:06:28.593,$GPGLL,4651.739,N,09153.857,W
10/05/2010,13:06:38.546,$GPGLL,4651.754,N,09153.828,W
10/05/2010,13:06:48.500,$GPGLL,4651.768,N,09153.800,W
"""

raw_gga_cols = ['date','time','hdr','sensor_time','latitude','NS','longitude','EW','nmea_quality','nsv','hdop','antenna_height','antenna_height_m','height_wgs84','height_wgs84_m']
raw_gll_cols = ['date','time','hdr','latitude','NS','longitude','EW']
raw_vtg_cols = ['date','time','hdr','heading_true','True','heading_mag','Mag','speed_kts','Knots','speed_kph','Kph']
raw_zda_cols = ['date','time','hdr','sensor_time','day','month','year','tz_hr','tz_min']

sensor_timestamp_format = "%H%M%S"
timestamp_format = "%m/%d/%Y %H:%M:%S.%f"

class Nav03Parser(NavParser):

    def __init__(self):
        super().__init__(name="nav03", description=description, example_data=example_data)


    @staticmethod
    def _hemisphere_correction(coordinate, hemisphere):
        if hemisphere in ('W', "S"):
            return coordinate * -1.0

        return coordinate


    def parse_file(self, filepath): # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """
        Process the provided file
        """

        # Line with parsing errors
        parse_error_lines = []

        pos_into_df = { 'iso_time': [], 'sensor_time': [], 'ship_latitude': [], 'ship_longitude': [], 'nmea_quality': [], 'nsv': [], 'hdop': [], 'antenna_height': [], 'valid_cksum': [] }
        
        try:
            with open(filepath, 'r') as csvfile:

                csvReader = csv.reader(csvfile)

                for row in csvReader:

                    if row[2] == '$GPGLL':

                        if len(row) != len(raw_gll_cols):
                            logging.warning("Parsing Error: (line: %s) %s" % (csvReader.line_num, ','.join(row)))
                            parse_error_lines.append(csvReader.line_num)
                            continue

                        try:
                            timestamp = datetime.strptime("%s %s" % (row[0], row[1]), timestamp_format)
                            ship_latitude = self._hemisphere_correction(float(row[3][:2]) + float(row[3][2:])/60, row[4])
                            ship_longitude = self._hemisphere_correction(float(row[5][:3]) + float(row[5][3:])/60, row[6])
                        except Exception as err:
                            logging.warning("Parsing Error: (line: %s) %s" % (csvReader.line_num, ','.join(row)))
                            logging.debug(str(err))
                            parse_error_lines.append(csvReader.line_num)
                            continue

                        pos_into_df['iso_time'].append(timestamp)
                        pos_into_df['sensor_time'].append(timestamp)
                        pos_into_df['ship_latitude'].append(ship_latitude)
                        pos_into_df['ship_longitude'].append(ship_longitude)
                        pos_into_df['nmea_quality'].append(1)
                        pos_into_df['nsv'].append(None)
                        pos_into_df['hdop'].append(None)
                        pos_into_df['antenna_height'].append(None)
                        pos_into_df['valid_cksum'].append(1)

                    elif row[2] == '$GPGGA':

                        if len(row) != len(raw_gga_cols):
                            logging.warning("Parsing Error: (line: %s) %s" % (csvReader.line_num, ','.join(row)))
                            parse_error_lines.append(csvReader.line_num)
                            continue

                        try:
                            timestamp = datetime.strptime("%s %s" % (row[0], row[1]), timestamp_format)
                            ship_latitude = self._hemisphere_correction(float(row[4][:2]) + float(row[4][2:])/60, row[5])
                            ship_longitude = self._hemisphere_correction(float(row[6][:3]) + float(row[6][3:])/60, row[7])
                            nmea_quality = int(row[8])
                            nsv = int(row[9])
                            hdop = float(row[10])
                            antenna_height = float(row[11])

                        except Exception as err:
                            logging.warning("Parsing Error: (line: %s) %s" % (csvReader.line_num, ','.join(row)))
                            logging.debug(str(err))
                            parse_error_lines.append(csvReader.line_num)
                            continue

                        pos_into_df['iso_time'].append(timestamp)
                        pos_into_df['sensor_time'].append(timestamp)
                        pos_into_df['ship_latitude'].append(ship_latitude)
                        pos_into_df['ship_longitude'].append(ship_longitude)
                        pos_into_df['nmea_quality'].append(nmea_quality)
                        pos_into_df['nsv'].append(nsv)
                        pos_into_df['hdop'].append(hdop)
                        pos_into_df['antenna_height'].append(antenna_height)
                        pos_into_df['valid_cksum'].append(1)

        except Exception as err:
            logging.error("Problem accessing input file: %s", filepath)
            logging.error(str(err))
            return None

        logging.debug("Finished parsing data file")

        return pos_into_df, parse_error_lines
