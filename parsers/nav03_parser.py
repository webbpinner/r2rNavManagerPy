#!/usr/bin/env python3
'''
        FILE:  nav03_parser.py
 DESCRIPTION:  Nav03 parser class for GLL data prefixed with the SCS formatted
               timestamp (mm/dd/YYYY,HH:MM:SS.sss) and comma (,).  Data may contain
               random NMEA0183 GGA, VTG and ZDA sentences.    None of the sentences
               contain trailing checksums.

        BUGS:
       NOTES:
      AUTHOR:  Webb Pinner
     COMPANY:  OceanDataTools
     VERSION:  0.2
     CREATED:  2021-04-27
    REVISION:  2021-05-05

LICENSE INFO: This code is licensed under MIT license (see LICENSE.txt for details)
              Copyright (C) OceanDataTools 2021
'''

import csv
import sys
import logging
from datetime import datetime

from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

from lib.nav_manager import NavParser
from lib.utils import hemisphere_correction

DESCRIPTION = "Nav parser for GLL data prefixed with the SCS formatted timestamp (mm/dd/YYYY,HH:MM:SS.sss) and comma (,).  Data may contain random NMEA0183 GGA, VTG and ZDA sentences.  None of the sentences contain trailing checksums."

EXAMPLE_DATA = """
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

TIMESTAMP_FORMAT = "%m/%d/%Y,%H:%M:%S.%f"

class Nav03Parser(NavParser):
    '''
    Parser class for GLL data prefixed with the SCS formatted timestamp
    (mm/dd/YYYY,HH:MM:SS.sss) and comma (,).  Data may contain random NMEA0183
    GGA, VTG and ZDA sentences.  None of the sentences contain trailing
    checksums.
    '''

    def __init__(self):
        super().__init__(name="nav03", description=DESCRIPTION, example_data=EXAMPLE_DATA)


    def parse_file(self, filepath): # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """
        Process the provided file
        """

        pos_into_df = { 'iso_time': [], 'sensor_time': [], 'ship_latitude': [], 'ship_longitude': [], 'nmea_quality': [], 'nsv': [], 'hdop': [], 'antenna_height': [], 'valid_cksum': [], 'valid_parse': [] }

        try:
            with open(filepath, 'r') as csvfile:

                csv_reader = csv.reader(csvfile)

                for row in csv_reader:

                    iso_time = None
                    sensor_time = None
                    ship_latitude = None
                    ship_longitude = None
                    nmea_quality = None
                    nsv = None
                    hdop = None
                    antenna_height = None
                    valid_cksum = None
                    valid_parse = 0

                    if row[2] == '$GPGLL':

                        if len(row) != len(raw_gll_cols):
                            logging.warning("Parsing Error: (line: %s) %s", csv_reader.line_num, ','.join(row))
                            valid_parse = 0

                        try:
                            timestamp = datetime.strptime(row[0] + ',' + row[1], TIMESTAMP_FORMAT)
                            ship_latitude = self.hemisphere_correction(float(row[3][:2]) + float(row[3][2:])/60, row[4])
                            ship_longitude = self.hemisphere_correction(float(row[5][:3]) + float(row[5][3:])/60, row[6])
                            nmea_quality = 1
                            valid_cksum = 1
                            valid_parse = 1

                        except Exception as err:
                            logging.warning("Parsing Error: (line: %s) %s", csv_reader.line_num, ','.join(row))
                            logging.debug(str(err))

                        pos_into_df['iso_time'].append(timestamp)
                        pos_into_df['sensor_time'].append(timestamp)
                        pos_into_df['ship_latitude'].append(ship_latitude)
                        pos_into_df['ship_longitude'].append(ship_longitude)
                        pos_into_df['nmea_quality'].append(nmea_quality)
                        pos_into_df['nsv'].append(nsv)
                        pos_into_df['hdop'].append(hdop)
                        pos_into_df['antenna_height'].append(antenna_height)
                        pos_into_df['valid_cksum'].append(valid_cksum)
                        pos_into_df['valid_parse'].append(valid_parse)

                    elif row[2] == '$GPGGA':

                        if len(row) != len(raw_gga_cols):
                            logging.warning("Parsing Error: (line: %s) %s", csv_reader.line_num, ','.join(row))

                        try:
                            timestamp = datetime.strptime("%s %s" % (row[0], row[1]), TIMESTAMP_FORMAT)
                            ship_latitude = self.hemisphere_correction(float(row[4][:2]) + float(row[4][2:])/60, row[5])
                            ship_longitude = self.hemisphere_correction(float(row[6][:3]) + float(row[6][3:])/60, row[7])
                            nmea_quality = int(row[8])
                            nsv = int(row[9])
                            hdop = float(row[10])
                            antenna_height = float(row[11])
                            valid_cksum = 1
                            valid_parse = 1

                        except Exception as err:
                            logging.warning("Parsing Error: (line: %s) %s", csv_reader.line_num, ','.join(row))
                            logging.debug(str(err))

                        pos_into_df['iso_time'].append(timestamp)
                        pos_into_df['sensor_time'].append(timestamp)
                        pos_into_df['ship_latitude'].append(ship_latitude)
                        pos_into_df['ship_longitude'].append(ship_longitude)
                        pos_into_df['nmea_quality'].append(nmea_quality)
                        pos_into_df['nsv'].append(nsv)
                        pos_into_df['hdop'].append(hdop)
                        pos_into_df['antenna_height'].append(antenna_height)
                        pos_into_df['valid_cksum'].append(valid_cksum)
                        pos_into_df['valid_parse'].append(valid_parse)

        except Exception as err:
            logging.error("Problem accessing input file: %s", filepath)
            logging.error(str(err))
            return None

        logging.debug("Finished parsing data file")

        return pos_into_df
