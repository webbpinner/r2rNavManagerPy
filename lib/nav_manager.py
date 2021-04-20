#!/usr/bin/env python3
# ----------------------------------------------------------------------------------- #
#
#         FILE:  nav_parser.py
#
#  DESCRIPTION:  Parent parser class for all nav parsers.
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
import sys
import json
import logging
import numpy as np
import pandas as pd
from rdp import rdp
from datetime import datetime, timedelta
from geopy import Point
from geopy.distance import great_circle

from os.path import dirname, realpath, basename
sys.path.append(dirname(dirname(realpath(__file__))))

from lib.utils import calculate_bearing, read_r2rnavfile
from lib.geocsv_templates import bestres_header, onemin_header, control_header

parse_cols = ['iso_time','ship_longitude','ship_latitude','nmea_quality','nsv','hdop','antenna_height','valid_cksum','sensor_time']

bestres_cols = ['iso_time','ship_longitude','ship_latitude','nmea_quality','nsv','hdop','antenna_height','speed_made_good','course_made_good']
onemin_cols = ['iso_time','ship_longitude','ship_latitude','speed_made_good','course_made_good']
control_cols = ['iso_time','ship_longitude','ship_latitude']

max_speed = 8.7  # m/s
max_accel = 1    # m/s^2
max_deltaT = 300 # seconds

rdp_epsilon = 0.001

rounding = {
    'ship_longitude': 8,
    'ship_latitude': 8,
    'speed_made_good': 2,
    'course_made_good': 3
}

class NpEncoder(json.JSONEncoder):
    """
    Custom JSON string encoder used to deal with NumPy arrays
    """
    def default(self, obj): # pylint: disable=arguments-differ

        if isinstance(obj, np.integer):
            return int(obj)

        if isinstance(obj, np.floating):
            return float(obj)

        if isinstance(obj, np.ndarray):
            return obj.tolist()

        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        return super().default(obj)


class NavInfoReport():
    """
    Class for a nav info reports
    """    

    def __init__(self, filename):
        self._filename = filename
        self._startTS = None
        self._endTS = None
        self._startCoord = [None, None]
        self._endCoord = [None, None]
        self._bbox = [ None, None, None, None]
        self._totalLines = None


    @property
    def filename(self):
        return self._filename
    

    @property
    def startTS(self):
        return self._startTS


    @property
    def endTS(self):
        return self._endTS


    @property
    def startCoord(self):
        return self._startCoord


    @property
    def endCoord(self):
        return self._endCoord


    @property
    def bbox(self):
        return self._bbox


    @property
    def totalLines(self):
        return self._totalLines


    def build_report(self, dataframe):
        self._startTS = dataframe['iso_time'].iloc[0]
        self._endTS = dataframe['iso_time'].iloc[-1]
        self._startCoord = [dataframe['ship_longitude'].iloc[0],dataframe['ship_latitude'].iloc[0]]
        self._endCoord = [dataframe['ship_longitude'].iloc[-1],dataframe['ship_latitude'].iloc[-1]]
        self._bbox = [dataframe['ship_longitude'].max(),dataframe['ship_latitude'].max(),dataframe['ship_longitude'].min(),dataframe['ship_latitude'].min()]
        self._totalLines = len(dataframe.index)


    def __str__(self):
        return "NavInfo Report: %s\n\
Navigation Start/End Info:\n\
\tStart Date: %s\n\
\tEnd Date: %s\n\
\tStart Lat/Lon: [%f,%f]\n\
\tEnd Lat/Lon: [%f,%f]\n\
Navigation Bounding Box Info:\n\
\tMinimum Longitude: %f\n\
\tMaximum Longitude: %f\n\
\tMinimum Latitude: %f\n\
\tMaximum Latitude: %f\n\
Total Lines of Data: %s\
" % (basename(self._filename), self._startTS.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), self._endTS.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), self._startCoord[1], self._startCoord[0], self._endCoord[1], self._endCoord[0], self._bbox[2], self._bbox[0], self._bbox[3], self._bbox[1], self._totalLines)


    def to_json(self):
        """
        Return test data object as a json-formatted string
        """
        return {"filename": self._filename, "startTS": self._startTS.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), "endTS": self._endTS.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), "startCoord": self._startCoord, "endCoord": self._endCoord, "bbox": self._bbox, "totalLines": self._totalLines}



class NavFileReport(NavInfoReport):
    """
    Class for a nav file reports
    """    

    def __init__(self, filename):
        super().__init__(filename=filename)
        self._parseErrors = []


    @property
    def parseErrors(self):
        return self._parseErrors
    

    def build_report(self, dataframe, parseErrors=[]):
        super().build_report(dataframe)
        self._parseErrors = parseErrors
        self._totalLines = len(dataframe.index) + len(parseErrors)


    def __str__(self):
        return "File Report: %s\n\
Navigation Start/End Info:\n\
\tStart Date: %s\n\
\tEnd Date: %s\n\
\tStart Lat/Lon: [%f,%f]\n\
\tEnd Lat/Lon: [%f,%f]\n\
Navigation Bounding Box Info:\n\
\tMinimum Longitude: %f\n\
\tMaximum Longitude: %f\n\
\tMinimum Latitude: %f\n\
\tMaximum Latitude: %f\n\
Parsing Errors: %d\n\
Total Lines of Data: %d\
" % (self._filename, self._startTS.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), self._endTS.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), self._startCoord[1], self._startCoord[0], self._endCoord[1], self._endCoord[0], self._bbox[2], self._bbox[0], self._bbox[3], self._bbox[1], len(self._parseErrors), self._totalLines)


    def to_json(self):
        """
        Return test data object as a json-formatted string
        """
        return {"filename": self._filename, "startTS": self._startTS.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), "endTS": self._endTS.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), "startCoord": self._startCoord, "endCoord": self._endCoord, "bbox": self._bbox, "parseErrors": self._parseErrors, "totalLines": self._totalLines}


class NavQAReport():
    """
    Class for a nav info reports
    """    

    def __init__(self, filename, deltaTThreshold = max_deltaT, speedThreshold = max_speed, accelerationThreshold = max_accel):

        # The filename
        self._filename = filename

        # Total data rows
        self._totalLines = None

        # The QA thresholds
        self._deltaTThreshold = pd.Timedelta('%d seconds' % deltaTThreshold)
        self._horizontalSpeedThreshold = speedThreshold
        self._horzontalAccelerationThreshold = accelerationThreshold

        # The QA min/max
        self._antennaAltitude = [ None, None ]
        self._horizontalSpeed = [ None, None ]
        self._horizontalAcceleration = [ None, None ]
        self._horizontalSpeed = [ None, None ]
        self._distanceFromPort = [ None, None ]
        self._timestamps = [ None, None ]
        self._satellites = [ None, None ]
        self._hdop = [ None, None ]
        self._deltaT = [ None, None ]

        # The QA errors
        self._deltaTErrors = None
        self._outOfSequenceError = None
        self._nmeaQualtyErrors = None
        self._horizontalSpeedErrors = None
        self._horizontalAccelerationErrors = None
        self._cksumErrors = None


    def build_report(self, dataframe):

        self._totalLines = len(dataframe.index)

        self._antennaAltitude = [ dataframe['antenna_height'].min(), dataframe['antenna_height'].max() ]
        self._horizontalSpeed = [ dataframe['speed_made_good'].min(), dataframe['speed_made_good'].max() ]
        self._horizontalAcceleration = [ dataframe['acceleration'].min(), dataframe['acceleration'].max() ]
        self._distanceFromPort = [ 0, 0 ]
        self._timestamps = [ dataframe['iso_time'].iloc[0], dataframe['iso_time'].iloc[-1] ]
        self._nsv = [ int(dataframe['nsv'].min()), int(dataframe['nsv'].max()) ]
        self._hdop = [ dataframe['hdop'].min(), dataframe['hdop'].max() ]
        self._deltaT = [ dataframe['deltaT'].min(), dataframe['deltaT'].max() ]

        self._deltaTErrors = len(dataframe[(dataframe['deltaT'] > self._deltaTThreshold)])
        self._outOfSequenceErrors = len(dataframe[(dataframe['valid_order'] == 0)])
        self._nmeaQualtyErrors = self._totalLines - len(dataframe[dataframe['nmea_quality'].between(1,3)])
        self._horizontalSpeedErrors = len(dataframe[(dataframe['speed_made_good'] > self._horizontalSpeedThreshold)])
        self._horizontalAccelerationErrors = len(dataframe[(dataframe['acceleration'] > self._horzontalAccelerationThreshold)])
        self._cksumErrors = len(dataframe[(dataframe['valid_cksum'] == 0)])


    def __str__(self):
        return "NavQA Report: %s\n\
Duration and range of values:\n\
Maximum Antenna Altitude: %0.3f m\n\
Minimum Antenna Altitude: %0.3f m\n\
Maximum Horizontal Speed: %0.3f m/s\n\
Minimum Horizontal Speed: %0.3f m/s\n\
Maximum Horizontal Acceleration: %0.3f m/s^2\n\
Minimum Horizontal Acceleration: %0.3f m/s^2\n\
Distance from Port Start: %0.2f m\n\
Distance from Port End: %0.2f m\n\
First epoch: %s\n\
Last epoch: %s\n\
Possible Number of Epochs with Observations:\n\
Actual Number of Epochs with Observations:\n\
Actual Countable Number of Epoch with Observations:\n\
Absent Number of Epochs with Observations:\n\
Flagged Number of Epochs with Observations:\n\
Number of satellites:\n\
Maximum Number of Satellites: %d\n\
Minimum Number of Satellites: %d\n\
Maximum HDOP: %0.1f\n\
Minimum HDOP: %0.1f\n\n\
Qualtiy Assessment:\n\
Longest epoch gap: %s\n\
Number of Gaps Longer than Threshold: %d\n\
Percentage of Gaps Longer than Threshold: %0.3f %%\n\
Number of Epochs Out of Sequence: %d\n\
Percent records out of sequence: %0.3f %%\n\
Number of Epochs with Bad GPS Quality Indicator: %d\n\
Percent records with Bad GPS Quality Indicator: %0.3f %%\n\
Number of Horizontal Speeds Exceeding Threshold: %d\n\
Percent Unreasonable Horizontal Speeds: %0.3f %%\n\
Number of Horizontal Accelerations Exceeding Threshold: %d\n\
Percent Unreasonable Horizontal Accelerations: %0.3f %%\n\
" % (basename(self._filename),
    self._antennaAltitude[1],
    self._antennaAltitude[0],
    self._horizontalSpeed[1],
    self._horizontalSpeed[0],
    self._horizontalAcceleration[1],
    self._horizontalAcceleration[0],
    self._distanceFromPort[0],
    self._distanceFromPort[1],
    self._timestamps[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    self._timestamps[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    self._nsv[1],
    self._nsv[0],
    self._hdop[1],
    self._hdop[0],
    str(self._deltaT[1]),
    self._deltaTErrors,
    round(100 * self._deltaTErrors/self._totalLines, 4),
    self._outOfSequenceErrors,
    round(100 * self._outOfSequenceErrors/self._totalLines, 4),
    self._nmeaQualtyErrors,
    round(100 * self._nmeaQualtyErrors/self._totalLines, 4),
    self._horizontalSpeedErrors,
    round(100 * self._horizontalSpeedErrors/self._totalLines, 4),
    self._horizontalAccelerationErrors,
    round(100 * self._horizontalAccelerationErrors/self._totalLines, 4),
)


    def to_json(self):
        """
        Return test data object as a json-formatted string
        """
        return {
            "filename": self._filename,
            "antennaAltitudeMax": self._antennaAltitude[1],
            "antennaAltitudeMin": self._antennaAltitude[0],
            "horizontalSpeedMax": self._horizontalSpeed[1],
            "horizontalSpeedMin": self._horizontalSpeed[0],
            "horizontalAccelerationMax": self._horizontalAcceleration[1],
            "horizontalAccelerationMin": self._horizontalAcceleration[0],
            "distanceFromStartPort": self._distanceFromPort[0],
            "distanceFromEndPort": self._distanceFromPort[1],
            "firstEpoch": self._timestamps[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "lastEpoch": self._timestamps[1].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "satellitesMax": self._nsv[1],
            "satellitesMin": self._nsv[0],
            "hdopMax": self._hdop[1],
            "hdopMin": self._hdop[0],
            "deltaTMax": str(self._deltaT[1]),
            "deltaTErrorPercentage": round(self._deltaTErrors/self._totalLines, 2) * 100,
            "outOfSequenceErrors": self._outOfSequenceErrors,
            "outOfSequenceErrorPercentage": round(self._outOfSequenceErrors/self._totalLines, 2) * 100,
            "nmeaQualtyErrors": self._nmeaQualtyErrors,
            "nmeaQualtyErrorPercentage": round(self._nmeaQualtyErrors/self._totalLines, 2) * 100,
            "horizontalSpeedErrors": self._horizontalSpeedErrors,
            "horizontalSpeedErrorPercentage": round(self._horizontalSpeedErrors/self._totalLines, 2) * 100,
            "horizontalAccelerationErrors": self._horizontalAccelerationErrors,
            "horizontalAccelerationErrorPercentage": round(self._horizontalAccelerationErrors/self._totalLines, 2) * 100
        }


class NavExport():
    """
    Class for a nav info reports
    """    

    def __init__(self, filename, deltaTThreshold = max_deltaT, speedThreshold = max_speed, accelerationThreshold = max_accel):

        # The filename
        self._filename = filename

        # The QA thresholds
        self._deltaTThreshold = pd.Timedelta('%d seconds' % deltaTThreshold)
        self._horizontalSpeedThreshold = speedThreshold
        self._horzontalAccelerationThreshold = accelerationThreshold

        self._geocsv_header = None

        self._data = None


    @property
    def data(self):
        return self._data
    

    @staticmethod
    def _round_data(data_frame, precision=None):
        """
        Round the data to the specified precision
        """
        if precision is None or bool(precision):
            try:
                decimals = pd.Series(precision.values(), index=precision.keys())
                return data_frame.round(decimals)
            except Exception as err:
                logging.error("Could not round data")
                logging.error(str(err))
                raise err
        return data_frame


    def read_r2rnavfile(self, file_format='csv'):
        self._data = read_r2rnavfile(self._filename, file_format)


    def crop_data(self, startTS=None, endTS=None):
        """
        Crop the dataframe to the start/end timestamps specified.
        """
        try:
            if startTS is not None:
                logging.debug("  start_dt: %s", startTS)
                self._data = self._data[(self._data['iso_time'] >= startTS)]

            if endTS is not None:
                logging.debug("  stop_dt: %s", endTS)
                self._data = self._data[(self._data['iso_time'] <= endTS)]

        except Exception as err:
            logging.error("Could not crop data")
            logging.error(str(err))
            raise err


    def apply_qc(self):

        # remove bad gps fixes
        logging.debug("Culling bad NMEA fixes")
        self._data = self._data[self._data['nmea_quality'].between(1,3)]

        # remove bad cksums
        logging.debug("Culling bad cksums")
        self._data = self._data[self._data['valid_cksum'] == 1]

        # remove bad sequence data points
        logging.debug("Culling out-of-sequence data")
        self._data = self._data[self._data['valid_order'] == 1]        
        
        # remove bad speeds
        logging.debug("Culling data exceeding speed threshold")
        self._data = self._data[self._data['speed_made_good'] <= self._horizontalSpeedThreshold]        
        
        # remove bad accelerations
        logging.debug("Culling data exceeding acceleration threshold")
        self._data = self._data[self._data['acceleration'] <= self._horzontalAccelerationThreshold]        


    def build_bestres(self):
        drop_columns = [x for x in list(self._data.columns) if x not in bestres_cols]
        logging.debug("Dropping columns: %s" % drop_columns)
        self._data = self._data.drop(drop_columns, axis = 1)

        logging.debug("Rounding data: %s", rounding)
        self._data = self._round_data(self._data, rounding)

        # Update geocsv header
        self._geocsv_header = bestres_header


    def build_1min(self):
        drop_columns = [x for x in list(self._data.columns) if x not in onemin_cols]
        logging.debug("Dropping columns: %s" % drop_columns)
        self._data = self._data.drop(drop_columns, axis = 1)

        logging.debug('Subsampling data...')
        self._data.set_index('iso_time',inplace=True)
        self._data = self._data.resample('1T', label='left', closed='left').first()
        self._data.reset_index(inplace=True)
        self._data.dropna(inplace=True, thresh=4)

        # Calculate deltaT column
        logging.debug('Building deltaT column...')
        self._data = self._data.join(self._data['iso_time'].diff().to_frame(name='deltaT'))

        # Calculate distance column
        logging.debug("Building distance column...")
        self._data['point'] = self._data.apply(lambda row: Point(latitude=row['ship_latitude'], longitude=row['ship_longitude']), axis=1)
        self._data['point_next'] = self._data['point'].shift(1)
        self._data.loc[self._data['point_next'].isna(), 'point_next'] = None

        self._data['distance'] = self._data.apply(lambda row: great_circle(row['point'], row['point_next']).km if row['point_next'] is not None else float('nan'), axis=1)

        # Calculate speed_made_good column
        logging.debug("Building speed_made_good column...")
        self._data['speed_made_good'] = (self._data['distance'] * 1000) / self._data.deltaT.dt.total_seconds()

        # Calculate course_made_good column
        logging.debug("Building course_made_good column...")
        self._data['course_made_good'] = self._data.apply(lambda row: calculate_bearing(tuple(row['point']), tuple(row['point_next'])) if row['point_next'] is not None else float('nan'), axis=1)

        self._data = self._data.drop('point_next', axis=1)
        self._data = self._data.drop('point', axis=1)
        self._data = self._data.drop('distance', axis=1)
        self._data = self._data.drop('deltaT', axis=1)

        logging.debug("Rounding data: %s", rounding)
        self._data = self._round_data(self._data, rounding)

        # Update geocsv header
        self._geocsv_header = onemin_header


    def build_control(self):
        drop_columns = [x for x in list(self._data.columns) if x not in control_cols]
        logging.debug("Dropping columns: %s" % drop_columns)
        self._data = self._data.drop(drop_columns, axis = 1)

        # run rdp algorithim
        logging.debug("Building control coordinates using RDP algorithim")
        coords = self._data.filter(['ship_longitude','ship_latitude'], axis=1).to_numpy()
        control = rdp(coords, epsilon=rdp_epsilon)

        logging.debug("Length of full-res coordinates: %d" % len(self._data.index))
        logging.debug("Length of control coordinates: %d" % control.shape[0])

        control_df = pd.DataFrame(control, columns = ['ship_longitude','ship_latitude'])

        self._data = pd.merge(control_df, self._data, on=['ship_longitude','ship_latitude'], how='left')
        self._data = self._data[control_cols]

        logging.debug("Rounding data: %s", rounding)
        self._data = self._round_data(self._data, rounding)

        # Update geocsv header
        self._geocsv_header = control_header


    def geocsv_header(self, custom_meta = None):

        geocsv_header = ""

        for key, value in self._geocsv_header.items():
            if custom_meta and key in custom_meta:
                geocsv_header += "#%s: %s\n" % (key, custom_meta[key])

            else:
                geocsv_header += "#%s: %s\n" % (key, self._geocsv_header[key])

        return geocsv_header


    def to_csv(self):
        output = StringIO()
        self._data.to_csv(output, index=False, na_rep='NAN')
        output.seek(0)
        print(output.read())

    def to_geocsv(self):
        # add header
        self.to_csv()

class NavParser():
    """
    Root Class for a nav parser object
    """

    def __init__(self, name, description=None, example_data=None):
        self._name = name
        self._description = description
        self._example_data = example_data
        self._parse_cols = parse_cols
        self._file_report = []
        self._df_proc = pd.DataFrame()


    @property
    def name(self):
        return self._name
    

    @property
    def description(self):
        return self._description
    

    @property
    def example_data(self):
        return self._example_data


    @property
    def parse_cols(self):
        return self._parse_cols
    

    @property
    def file_report(self):
        return self._file_report
        

    @property
    def dataframe(self):
        return self._df_proc


    def parse_file(self, filepath):
        """
        Process the given file
        """
        raise NotImplementedError('process_file must be implemented by subclass')


    def add_file_report(self, file_report):
        self._file_report.append(file_report)


    def add_dateframe(self, df):
        if self._df_proc.empty:
            self._df_proc = df
        else:
            self._df_proc = pd.concat([self._df_proc, df], ignore_index=True)


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
        self._df_proc['point'] = self._df_proc.apply(lambda row: Point(latitude=row['ship_latitude'], longitude=row['ship_longitude']), axis=1)
        self._df_proc['point_next'] = self._df_proc['point'].shift(1)
        self._df_proc.loc[self._df_proc['point_next'].isna(), 'point_next'] = None

        self._df_proc['distance'] = self._df_proc.apply(lambda row: great_circle(row['point'], row['point_next']).km if row['point_next'] is not None else float('nan'), axis=1)

        # Calculate speed_made_good column
        logging.debug("Building speed_made_good column...")
        self._df_proc['speed_made_good'] = (self._df_proc['distance'] * 1000) / self._df_proc['sensor_deltaT'].dt.total_seconds()

        # Calculate course_made_good column
        logging.debug("Building course_made_good column...")
        self._df_proc['course_made_good'] = self._df_proc.apply(lambda row: calculate_bearing(tuple(row['point']), tuple(row['point_next'])) if row['point_next'] is not None else float('nan'), axis=1)

        self._df_proc = self._df_proc.drop('point_next', axis=1)
        self._df_proc = self._df_proc.drop('point', axis=1)

        # Calculate acceleration column
        logging.debug("Building acceleration column...")
        self._df_proc['speed_next'] = self._df_proc['speed_made_good'].shift(1)
        self._df_proc.loc[self._df_proc['speed_next'].isna(), 'speed_next'] = None
        self._df_proc['acceleration'] = (self._df_proc['speed_made_good'] - self._df_proc['speed_next']) / self._df_proc.deltaT.dt.total_seconds()
        self._df_proc = self._df_proc.drop('speed_next', axis=1)


    def crop_data(self, startTS=None, endTS=None):
        """
        Crop the dataframe to the start/end timestamps specified.
        """
        try:
            if startTS is not None:
                logging.debug("  start_dt: %s", startTS)
                self._df_proc = self._df_proc[(self._df_proc['iso_time'] >= startTS)]

            if endTS is not None:
                logging.debug("  stop_dt: %s", endTS)
                self._df_proc = self._df_proc[(self._df_proc['iso_time'] <= endTS)]

        except Exception as err:
            logging.error("Could not crop data")
            logging.error(str(err))
            raise err
