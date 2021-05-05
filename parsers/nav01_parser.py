#!/usr/bin/env python3
'''
        FILE:  nav01_parser.py
 DESCRIPTION:  Nav01 parser class for raw output from a Furuno GP-90D GPS reciever
               Data file contains GGA/ZDA/VTG NMEA0183 sentences with no additional
               information added.

        BUGS:
       NOTES:
      AUTHOR:  Webb Pinner
     COMPANY:  OceanDataTools
     VERSION:  0.2
     CREATED:  2021-04-24
    REVISION:  2021-05-05

LICENSE INFO: This code is licensed under MIT license (see LICENSE.txt for details)
              Copyright (C) OceanDataTools 2021
'''

import re
import csv
import sys
import logging
from datetime import datetime, timedelta

from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

import pandas as pd
from geopy import Point
from geopy.distance import distance

from lib.nav_manager import NavParser
from lib.utils import calculate_bearing

DESCRIPTION = "Nav parser for raw output from a Furuno GP-90D GPS reciever. Data file contains GGA/ZDA/VTG NMEA0183 sentences with no additional information added."

EXAMPLE_DATA = """
$GPGGA,123034,2447.9660,N,12221.8670,E,2,9,0.3,38,M,,M,,*40
$GPVTG,147.2,T,150.9,M,7.6,N,14.1,K*76
$GPZDA,123034,23,08,2009,00,00*4D
$GPGGA,123035,2447.9641,N,12221.8681,E,2,9,0.4,38,M,,M,,*4B
$GPVTG,147.2,T,150.9,M,7.6,N,14.1,K*76
$GPZDA,123035,23,08,2009,00,00*4C
"""

raw_gga_cols = ['hdr','sensor_time','latitude','NS','longitude','EW','nmea_quality','nsv','hdop','antenna_height','antenna_height_m','height_wgs84','height_wgs84_m','last_update','dgps_station_checksum']
raw_vtg_cols = ['hdr','heading_true','True','heading_mag','Mag','speed_kts','Knots','speed_kph','Kph_checksum']
raw_zda_cols = ['hdr','sensor_time','day','month','year','tz_hr','tz_min_checksum']

SENSOR_TIMESTAMP_FORMAT = "%H%M%S"

class Nav01Parser(NavParser):
    '''
    Parser class for raw output from a Furuno GP-90D GPS reciever Data file
    contains GGA/ZDA/VTG NMEA0183 sentences with no additional information
    added.
    '''

    def __init__(self):
        super().__init__(name="nav01", description=DESCRIPTION, example_data=EXAMPLE_DATA)


    @staticmethod
    def _hemisphere_correction(coordinate, hemisphere):
        if hemisphere in ('W', "S"):
            return coordinate * -1.0

        return coordinate


    @staticmethod
    def _verify_checksum(sentence):
        cksum = sentence[len(sentence) - 2:]
        chksumdata = re.sub("(\n|\r\n)","", sentence[sentence.find("$")+1:sentence.find("*")])

        csum = 0

        for char in chksumdata:
            # XOR'ing value of csum against the next char in line
            # and storing the new XOR value in csum
            csum ^= ord(char)

        return 1 if hex(csum) == hex(int(cksum, 16)) else 0


    def parse_file(self, filepath): # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """
        Process the provided file
        """

        # Line with parsing errors
        parse_error_lines = []

        zda_into_df = { 'lineno': [], 'date': [] }
        vtg_into_df = { 'lineno': [], 'speed_made_good': [], 'course_made_good': [] }
        gga_into_df = { 'lineno': [], 'sensor_time': [], 'ship_latitude': [], 'ship_longitude': [], 'nmea_quality': [], 'nsv': [], 'hdop': [], 'antenna_height': [], 'valid_cksum': [] }

        try:
            with open(filepath, 'r') as csvfile:

                csv_reader = csv.reader(csvfile)

                for row in csv_reader:

                    if row[0] == '$GPZDA':

                        if len(row) != len(raw_zda_cols):
                            logging.warning("Parsing Error: (line: %s) %s", csv_reader.line_num, ','.join(row))
                            parse_error_lines.append(csv_reader.line_num)
                            continue

                        try:
                            date = datetime.strptime(row[4] + row[3] + row[2], "%Y%m%d")
                        except Exception as err:
                            logging.warning("Parsing Error: (line: %s) %s", csv_reader.line_num, ','.join(row))
                            logging.debug(str(err))
                            parse_error_lines.append(csv_reader.line_num)
                            continue

                        zda_into_df['lineno'].append(csv_reader.line_num)
                        zda_into_df['date'].append(date)

                    elif row[0] == '$GPVTG':

                        if len(row) != len(raw_vtg_cols):
                            logging.warning("Parsing Error: (line: %s) %s", csv_reader.line_num, ','.join(row))
                            parse_error_lines.append(csv_reader.line_num)
                            continue

                        try:
                            speed_made_good = float(row[7])*1000/3600
                            course_made_good = float(row[1])
                        except Exception as err:
                            logging.warning("Parsing Error: (line: %s) %s", csv_reader.line_num, ','.join(row))
                            logging.debug(str(err))
                            parse_error_lines.append(csv_reader.line_num)
                            continue

                        vtg_into_df['lineno'].append(csv_reader.line_num)
                        vtg_into_df['speed_made_good'].append(speed_made_good)
                        vtg_into_df['course_made_good'].append(course_made_good)

                    elif row[0] == '$GPGGA':

                        if len(row) != len(raw_gga_cols):
                            logging.warning("Parsing Error: (line: %s) %s", csv_reader.line_num, ','.join(row))
                            parse_error_lines.append(csv_reader.line_num)
                            continue

                        try:
                            sensor_time = datetime.strptime(row[1], SENSOR_TIMESTAMP_FORMAT)
                            ship_latitude = self._hemisphere_correction(float(row[2][:2]) + float(row[2][2:])/60, row[3])
                            ship_longitude = self._hemisphere_correction(float(row[4][:3]) + float(row[4][3:])/60, row[5])
                            nmea_quality = int(row[6])
                            nsv = int(row[7])
                            hdop = float(row[8])
                            antenna_height = float(row[9])
                            valid_cksum = self._verify_checksum(','.join(row))

                        except Exception as err:
                            logging.warning("Parsing Error: (line: %s) %s", csv_reader.line_num, ','.join(row))
                            logging.debug(str(err))
                            parse_error_lines.append(csv_reader.line_num)
                            continue

                        gga_into_df['lineno'].append(csv_reader.line_num)
                        gga_into_df['sensor_time'].append(sensor_time)
                        gga_into_df['ship_latitude'].append(ship_latitude)
                        gga_into_df['ship_longitude'].append(ship_longitude)
                        gga_into_df['nmea_quality'].append(nmea_quality)
                        gga_into_df['nsv'].append(nsv)
                        gga_into_df['hdop'].append(hdop)
                        gga_into_df['antenna_height'].append(antenna_height)
                        gga_into_df['valid_cksum'].append(valid_cksum)

        except Exception as err:
            logging.error("Problem accessing input file: %s", filepath)
            logging.error(str(err))
            return None

        zda_df = pd.DataFrame(zda_into_df)
        del zda_into_df
        zda_df.drop_duplicates(subset=['date'], keep='first', inplace=True)

        vtg_df = pd.DataFrame(vtg_into_df)
        del vtg_into_df

        gga_df = pd.DataFrame(gga_into_df)
        del gga_into_df

        # Merge GGA with VTG to create data
        data = pd.merge_asof(gga_df, vtg_df, on="lineno", direction="forward")

        # Merge data with ZDA
        data = pd.merge_asof(data, zda_df, on="lineno")

        # Drop rows where date could not be determined
        data = data[data['date'].notna()]

        # Use date and sensor_time to calculate iso_time
        data['iso_time'] = data['date'] + (data['sensor_time'] - datetime(1900, 1, 1))

        # Drop unnecessary columns
        data = data.drop(['lineno', 'date'], axis=1)

        # Re-order columns
        data = data[['iso_time', 'sensor_time', 'ship_latitude', 'ship_longitude', 'nmea_quality', 'nsv', 'hdop', 'antenna_height', 'valid_cksum', 'speed_made_good', 'course_made_good' ]]

        logging.debug("Finished parsing data file")

        return data, parse_error_lines

    def proc_dataframe(self):
        """
        Process the dataframe to calculate deltaT, distance, bearing, velocity,
        and acceleration
        """

        # Calculate deltaT column
        logging.debug('Building deltaT column...')
        self._df_proc = self._df_proc.join(self._df_proc['iso_time'].diff().to_frame(name='deltaT'))

        # Calculate sensor deltaT column
        logging.debug('Building sensor deltaT column...')
        self._df_proc = self._df_proc.join(self._df_proc['sensor_time'].diff().to_frame(name='sensor_deltaT'))

        # If sensor_time does not have a date (i.e. GGA/GLL), set day offset to
        # 0, this gets around files spanning multiple days
        self._df_proc['sensor_deltaT'] = self._df_proc.apply(lambda row: row['sensor_deltaT'] + timedelta(days=1) if row['sensor_time'].year == 1900 and row['sensor_deltaT'].days == -1 else row['sensor_deltaT'], axis=1)

        # If iso_time or sensor_time is negative flag as bad
        logging.debug("Flagging rows that may be out-of-sequence...")
        self._df_proc['valid_order'] = self._df_proc.apply(lambda row: 1 if pd.isnull(row['deltaT']) or row['deltaT'] > timedelta() and pd.isnull(row['sensor_deltaT']) or row['sensor_deltaT'] > timedelta() else 0, axis=1)

        # Calculate distance column
        logging.debug("Building distance column...")
        self._df_proc['distance'] = self._df_proc.apply(lambda row: row['speed_made_good'] / 1000 * row['sensor_deltaT'].total_seconds() if row['speed_made_good'] is not None and row['sensor_deltaT'] is not None else float('nan'), axis=1)

        self._df_proc['point'] = self._df_proc.apply(lambda row: Point(latitude=row['ship_latitude'], longitude=row['ship_longitude']), axis=1)
        self._df_proc['point_next'] = self._df_proc['point'].shift(1)
        self._df_proc.loc[self._df_proc['point_next'].isna(), 'point_next'] = None
        self._df_proc['distance'] = self._df_proc.apply(lambda row: distance(row['point'], row['point_next']).km if pd.isnull(row['distance']) and not pd.isnull(row['point_next']) else row['distance'], axis=1)

        # Calculate speed_made_good column
        logging.debug("Calculating missing values from speed_made_good column...")
        self._df_proc['speed_made_good'] = self._df_proc.apply(lambda row: row['distance'] * 1000 / row['sensor_deltaT'].total_seconds() if pd.isnull(row['speed_made_good']) and row['sensor_deltaT'] is not None else row['speed_made_good'], axis=1)

        # Calculate course_made_good column
        logging.debug("Calculating missing values course_made_good column...")
        self._df_proc['course_made_good'] = self._df_proc.apply(lambda row: calculate_bearing(tuple(row['point']), tuple(row['point_next'])) if pd.isnull(row['course_made_good']) and row['point_next'] is not None else row['course_made_good'], axis=1)

        self._df_proc = self._df_proc.drop('point_next', axis=1)
        self._df_proc = self._df_proc.drop('point', axis=1)

        # Calculate acceleration column
        logging.debug("Building acceleration column...")
        self._df_proc['speed_next'] = self._df_proc['speed_made_good'].shift(1)
        self._df_proc.loc[self._df_proc['speed_next'].isna(), 'speed_next'] = None
        self._df_proc['acceleration'] = (self._df_proc['speed_made_good'] - self._df_proc['speed_next']) / self._df_proc['sensor_deltaT'].dt.total_seconds()
        self._df_proc = self._df_proc.drop('speed_next', axis=1)

        # Reorder the dataframe columns to match the r2rnav format spec.
        self._df_proc = self._df_proc[['iso_time','ship_longitude','ship_latitude','nmea_quality','nsv','hdop','antenna_height','valid_cksum','sensor_time','deltaT','sensor_deltaT','valid_order','distance','speed_made_good','course_made_good','acceleration']]
