#!/usr/bin/env python3
# ----------------------------------------------------------------------------------- #
#
#         FILE:  nav33_parser.py
#
#  DESCRIPTION:  Nav33 parser class for GGA data prefixed with a ISO8601 formatted
#                timestamp (YYYY-mm-ddTHH:MM:SS.sssZ) and comma (,)
#
#         BUGS:
#        NOTES:
#       AUTHOR:  Webb Pinner
#      COMPANY:  OceanDataTools
#      VERSION:  0.1
#      CREATED:  2021-04-15
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
from datetime import datetime

from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

from lib.nav_manager import NavParser

description = "Nav parser for GGA data prefixed with a ISO8601 formatted timestamp (YYYY-mm-ddTHH:MM:SS.sssZ) and comma (,)"

example_data = """
2021-03-26T13:47:51.329619Z,$INGGA,134751.20,1911.031052,N,06918.538133,W,2,12,0.8,0.03,M,-42.58,M,12.0,0043*5A
2021-03-26T13:47:52.207173Z,$INGGA,134752.20,1911.030998,N,06918.538134,W,2,12,0.8,-0.01,M,-42.58,M,13.0,0043*7E
2021-03-26T13:47:53.212068Z,$INGGA,134753.20,1911.030936,N,06918.538141,W,2,12,0.8,-0.08,M,-42.58,M,14.0,0043*77
"""

raw_cols = ['timestamp','hdr','sensor_time','latitude','NS','longitude','EW','nmea_quality','nsv','hdop','antenna_height','antenna_height_m','height_wgs84','height_wgs84_m','last_update','dgps_station_checksum']

timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ" # ISO8601

sensor_timestamp_format = "%H%M%S.%f"

class Nav33Parser(NavParser):

    def __init__(self):
        super().__init__(name="nav33", description=description, example_data=example_data)
        self._raw_cols = raw_cols
        self._timestamp_format = timestamp_format


    @staticmethod
    def _hemisphere_correction(coordinate, hemisphere):
        if hemisphere in ('W', "S"):
            return coordinate * -1.0

        return coordinate


    @staticmethod
    def _verify_checksum(line):
        sentence = ",".join([v for k, v in line.items()][1:])
        cksum = sentence[len(sentence) - 2:]
        chksumdata = re.sub("(\n|\r\n)","", sentence[sentence.find("$")+1:sentence.find("*")])

        csum = 0

        for c in chksumdata:
           # XOR'ing value of csum against the next char in line
           # and storing the new XOR value in csum
           csum ^= ord(c)

        return 1 if hex(csum) == hex(int(cksum, 16)) else 0


    def parse_file(self, filepath): # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """
        Process the provided file
        """

        # Line with parsing errors
        parse_error_lines = []

        # Empty array to populate with parsed data
        raw_into_df = { value: [] for key, value in enumerate(self._parse_cols) }

        try:
            with open(filepath, 'r') as csvfile:
                reader = csv.DictReader(csvfile, self._raw_cols)

                for lineno, line in enumerate(reader):

                    try:

                        timestamp = datetime.strptime(line['timestamp'], self._timestamp_format)
                        sensor_timestamp = datetime.strptime(line['sensor_time'], sensor_timestamp_format)
                        latitude = (self._hemisphere_correction(float(line['latitude'][:2]) + float(line['latitude'][2:])/60, line['NS']))
                        longitude = (self._hemisphere_correction(float(line['longitude'][:3]) + float(line['longitude'][3:])/60, line['EW']))
                        nmea_quality = int(line['nmea_quality'])
                        nsv = int(line['nsv'])
                        hdop = float(line['hdop'])
                        antenna_height = float(line['antenna_height'])
                        valid_cksum = self._verify_checksum(line)

                    except Exception as err:
                        parse_error_lines.append(lineno)
                        logging.warning("Parsing error encountered on line %s", lineno)
                        logging.debug(line)
                        logging.debug(str(err))

                    else:
                        raw_into_df['iso_time'].append(timestamp)
                        raw_into_df['sensor_time'].append(sensor_timestamp)
                        raw_into_df['ship_latitude'].append(latitude)
                        raw_into_df['ship_longitude'].append(longitude)
                        raw_into_df['nmea_quality'].append(nmea_quality)
                        raw_into_df['nsv'].append(nsv)
                        raw_into_df['hdop'].append(hdop)
                        raw_into_df['antenna_height'].append(antenna_height)
                        raw_into_df['valid_cksum'].append(valid_cksum)

        except Exception as err:
            logging.error("Problem accessing input file: %s", filepath)
            logging.error(str(err))
            return None

        logging.debug("Finished parsing data file")

        return raw_into_df, parse_error_lines