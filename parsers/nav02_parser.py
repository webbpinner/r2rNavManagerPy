#!/usr/bin/env python3
'''
        FILE:  nav02_parser.py
 DESCRIPTION:  Nav02 parser class for GGA data prefixed with the SCS formatted
               timestamp (mm/dd/YYYY,HH:MM:SS.sss) and comma (,)

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

import re
import csv
import sys
import logging
from datetime import datetime

from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

from lib.nav_manager import NavParser
from lib.utils import hemisphere_correction, verify_checksum

DESCRIPTION = "Nav parser for GGA data prefixed with the SCS formatted timestamp (mm/dd/YYYY,HH:MM:SS.sss) and comma (,)"

EXAMPLE_DATA = """
03/19/2019,13:13:02.354,$GNGGA,131302.00,2443.628838,N,11858.560367,W,2,15,0.8,-25.400,M,0.000,M,6.0,0436*60
03/19/2019,13:13:02.854,$GNGGA,131302.50,2443.629467,N,11858.561860,W,2,15,0.8,-25.495,M,0.000,M,4.0,0436*61
03/19/2019,13:13:03.368,$GNGGA,131303.00,2443.630108,N,11858.563351,W,2,15,0.8,-25.594,M,0.000,M,4.0,0436*6A
"""

raw_cols = ['date','time','hdr','sensor_time','latitude','NS','longitude','EW','nmea_quality','nsv','hdop','antenna_height','antenna_height_m','height_wgs84','height_wgs84_m','last_update','dgps_station_checksum'] # SCS style

TIMESTAMP_FORMAT = "%m/%d/%Y,%H:%M:%S.%f"

SENSOR_TIMESTAMP_FORMAT = "%H%M%S.%f"

class Nav02Parser(NavParser):
    '''
    Parser class for GGA data prefixed with the SCS formatted timestamp
    (mm/dd/YYYY,HH:MM:SS.sss) and comma (,)
    '''

    def __init__(self):
        super().__init__(name="nav02", description=DESCRIPTION, example_data=EXAMPLE_DATA)
        self._raw_cols = raw_cols


    def parse_file(self, filepath): # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """
        Process the provided file
        """

        # Empty array to populate with parsed data
        raw_into_df = { value: [] for key, value in enumerate(self._parse_cols) }

        try:
            with open(filepath, 'r') as csvfile:
                reader = csv.DictReader(csvfile, self._raw_cols)

                for lineno, line in enumerate(reader):

                    try:

                        timestamp = datetime.strptime("%s,%s" % (line['date'], line['time']), TIMESTAMP_FORMAT)
                        sensor_timestamp = datetime.strptime(line['sensor_time'], SENSOR_TIMESTAMP_FORMAT)
                        latitude = (hemisphere_correction(float(line['latitude'][:2]) + float(line['latitude'][2:])/60, line['NS']))
                        longitude = (hemisphere_correction(float(line['longitude'][:3]) + float(line['longitude'][3:])/60, line['EW']))
                        nmea_quality = int(line['nmea_quality'])
                        nsv = int(line['nsv'])
                        hdop = float(line['hdop'])
                        antenna_height = float(line['antenna_height'])
                        valid_cksum = verify_checksum(line)

                    except Exception as err:

                        logging.warning("Parsing Error: (line: %s) %s", lineno, line)
                        logging.debug(str(err))
                        raw_into_df['iso_time'].append(None)
                        raw_into_df['sensor_time'].append(None)
                        raw_into_df['ship_latitude'].append(None)
                        raw_into_df['ship_longitude'].append(None)
                        raw_into_df['nmea_quality'].append(None)
                        raw_into_df['nsv'].append(None)
                        raw_into_df['hdop'].append(None)
                        raw_into_df['antenna_height'].append(None)
                        raw_into_df['valid_cksum'].append(None)
                        raw_into_df['valid_parse'].append(0)

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
                        raw_into_df['valid_parse'].append(1)

        except Exception as err:
            logging.error("Problem accessing input file: %s", filepath)
            raise err
            logging.error(str(err))
            return None

        logging.debug("Finished parsing data file")

        return raw_into_df
