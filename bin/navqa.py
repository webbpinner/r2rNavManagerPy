#!/usr/bin/env python3
'''
        FILE:  navqa.py
 DESCRIPTION:  Return quality assurance information based on r2rnav formatted file to
               stdout unless -l defined.

        BUGS:
       NOTES:
      AUTHOR:  Webb Pinner
     COMPANY:  OceanDataTools
     VERSION:  0.2
     CREATED:  2021-04-17
    REVISION:  2021-05-05

LICENSE INFO: This code is licensed under MIT license (see LICENSE.txt for details)
              Copyright (C) OceanDataTools 2021
'''

import argparse
import os
import sys
import json
import logging
from datetime import datetime

from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

from lib.utils import read_r2rnavfile
from lib.nav_manager import NavQAReport, MAX_DELTA_T, MAX_SPEED, MAX_ACCEL

# -------------------------------------------------------------------------------------
# Main function
# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Return quality assurance information based on r2rnav formatted file')
    parser.add_argument('-v', '--verbosity', dest='verbosity', default=0, action='count', help='Increase output verbosity, default level: warning')
    parser.add_argument('-l', '--logfile', type=str, metavar='logfile', help='Write output to specified logfile')
    parser.add_argument('-L', '--logfileformat', type=str, metavar='logfileformat', default="text", choices=["text","json"], help='The format of the logfile: text, json, default: text')
    parser.add_argument('--startTS', type=lambda d: datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%fZ'), metavar='startTS', help='Crop data to start timestamp, format: YYYY-mm-ddTHH:MM:SS.sssZ')
    parser.add_argument('--endTS', type=lambda d: datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%fZ'), metavar='endTS', help='Crop data to end timestamp, format: YYYY-mm-ddTHH:MM:SS.sssZ')
    parser.add_argument('-g', '--gapthreshold', type=float, default=MAX_DELTA_T,  metavar='gapthreshold', help='Set custom gap threshold in seconds')
    parser.add_argument('-s', '--speedthreshold', type=float, default=MAX_SPEED, metavar='speedthreshold', help='Set custom speed threshold in m/s')
    parser.add_argument('-a', '--accelerationthreshold', default=MAX_ACCEL, type=float, metavar='accelerationthreshold', help='Set custom acceleration threshold in m/s^2')
    parser.add_argument('-I', '--inputformat', type=str, metavar='inputformat', default="csv", choices=["csv","hdf"], help='The format type of input file: csv, hdf, default: csv')
    parser.add_argument('input', type=str, help='The input r2rnav file')

    parsed_args = parser.parse_args()

    ############################
    # Set up logging before we do any other argument parsing (so that we
    # can log problems with argument parsing).

    LOGGING_FORMAT = '%(asctime)-15s %(levelname)s - %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT)

    LOG_LEVELS = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
    parsed_args.verbosity = min(parsed_args.verbosity, max(LOG_LEVELS))
    logging.getLogger().setLevel(LOG_LEVELS[parsed_args.verbosity])

    try:

        # Process the files
        logging.info("Reading r2rnav file: %s", parsed_args.input)
        data = read_r2rnavfile(parsed_args.input, parsed_args.inputformat)

        if data is None:
            logging.error("Unable to read input file")
            sys.exit(0)

        try:
            if parsed_args.startTS:
                logging.info("Cropping data older than: %s", parsed_args.startTS)
                data = data[(data['iso_time'] >= parsed_args.startTS)]

            if parsed_args.endTS:
                logging.info("Cropping data newer than: %s", parsed_args.endTS)
                data = data[(data['iso_time'] <= parsed_args.endTS)]

        except Exception as err:
            logging.error("Error cropping data")
            logging.error(str(err))
            raise err

        if (parsed_args.startTS or parsed_args.endTS) and data.shape[0] == 0:
            logging.warning("Data is empty after cropping for start/end timestamps")
            sys.exit(0)

        logging.info("Compiling nav info")

        navqa = NavQAReport(parsed_args.input, delta_t_threshold=parsed_args.gapthreshold, speed_threshold=parsed_args.speedthreshold, acceleration_threshold=parsed_args.accelerationthreshold)
        navqa.build_report(data)

        if parsed_args.logfile:
            logging.info("Saving qa report to %s in %s format", parsed_args.logfile, parsed_args.logfileformat)

            try:
                with open(parsed_args.logfile, 'w') as log_file:

                    if parsed_args.logfileformat == 'text':
                        log_file.write(str(navqa))

                    elif parsed_args.logfileformat == 'json':
                        json.dump(navqa.to_json(), log_file, indent=2)

            except IOError:
                logging.error("Error saving qa report file: %s", parsed_args.logfile)

        else:
            logging.info("Send navqa to stdout in %s format", parsed_args.logfileformat)

            if parsed_args.logfileformat == 'text':
                print(navqa)

            elif parsed_args.logfileformat == 'json':
                json.dump(navqa.to_json(), log_file, indent=2)

    except KeyboardInterrupt:
        logging.warning('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0) #pylint: disable=protected-access
