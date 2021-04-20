#!/usr/bin/env python3
# ----------------------------------------------------------------------------------- #
#
#         FILE:  navexport.py
#
#  DESCRIPTION:  Export r2r nav products based on r2rnav formated file to stdout unless -l
#                defined.
#
#         BUGS:
#        NOTES:
#       AUTHOR:  Webb Pinner
#      COMPANY:  OceanDataTools
#      VERSION:  0.1
#      CREATED:  2021-04-17
#     REVISION:  
#
# LICENSE INFO: This code is licensed under MIT license (see LICENSE.txt for details)
#               Copyright (C) OceanDataTools 2021
#
# ----------------------------------------------------------------------------------- #

import argparse
import os
import sys
import json
import logging
import pandas as pd
from io import StringIO
from datetime import datetime

from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

from lib.utils import read_r2rnavfile
from lib.nav_manager import NavExport, max_deltaT, max_speed, max_accel

# -------------------------------------------------------------------------------------
# Required python code for running the script as a stand-alone utility
# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export r2r nav products based on r2rnav formated file')
    parser.add_argument('-v', '--verbosity', dest='verbosity', default=0, action='count', help='Increase output verbosity')
    parser.add_argument('-o', '--outfile', type=str, metavar='outfile', help='write output to specified outfile')
    parser.add_argument('-O', '--outfileformat', type=str, metavar='outfileformat', default="geocsv", choices=["csv","geocsv"], help='outfile format')
    parser.add_argument('-m', '--meta', type=str, metavar='metadatafile', nargs='*', help='custom metadata for geocsv header, overrides default vaules, format: "key=value"')
    parser.add_argument('-q', '--qc', action='store_true', help='exclude bad data points')
    parser.add_argument('-t', '--type', type=str, metavar='outputtype', default="bestres", choices=["bestres","1min","control"], help='type of output to generate')    
    parser.add_argument('--startTS', type=lambda d: datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%fZ'), metavar='startTS', help='crop data to start timestamp')
    parser.add_argument('--endTS', type=lambda d: datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%fZ'), metavar='endTS', help='crop data to end timestamp')
    parser.add_argument('-g', '--gapthreshold', type=float, default=max_deltaT,  metavar='gapthreshold', help='gap threshold in seconds')
    parser.add_argument('-s', '--speedthreshold', type=float, default=max_speed, metavar='speedthreshold', help='speed threshold in m/s')
    parser.add_argument('-a', '--accelerationthreshold', default=max_accel, type=float, metavar='accelerationthreshold', help='acceleration threshold in m/s^2')
    parser.add_argument('-I', '--inputformat', type=str, metavar='inputformat', default="csv", choices=["csv","hdf"], help='format type of input file')
    parser.add_argument('input', type=str, help='input r2rnav file')

    parsed_args = parser.parse_args()

    ############################
    # Set up logging before we do any other argument parsing (so that we
    # can log problems with argument parsing).
  
    LOGGING_FORMAT = '%(asctime)-15s %(levelname)s - %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT)

    LOG_LEVELS = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
    parsed_args.verbosity = min(parsed_args.verbosity, max(LOG_LEVELS))
    logging.getLogger().setLevel(LOG_LEVELS[parsed_args.verbosity])

    navexport = NavExport(parsed_args.input, deltaTThreshold=parsed_args.gapthreshold, speedThreshold=parsed_args.speedthreshold, accelerationThreshold=parsed_args.accelerationthreshold)


    try:

        try:
            # Process the files
            logging.info("Reading r2rnav file: %s" % parsed_args.input)
            navexport.read_r2rnavfile(parsed_args.inputformat)
        except Exception as err:
            logging.error("Unable to read input file")        
            raise err

        custom_meta = { 'creation_date': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") }

        if parsed_args.meta:
            for data in parsed_args.meta:
                key, value = data.split('=')
                custom_meta[key] = value

        logging.debug("Custom meta: %s" % custom_meta)

        if parsed_args.startTS or parsed_args.endTS:
            try:
                logging.info("Cropping data older than: %s", parsed_args.startTS)
                navexport.crop_data(startTS=parsed_args.startTS, endTS=parsed_args.endTS)

            except Exception as err:
                logging.error("Error cropping data")
                logging.error(str(err))
                raise err

            if navexport.data.shape[0] == 0:
                logging.warning("Data is empty after cropping for start/end timestamps")
                sys.exit(0)

        if parsed_args.qc:
            logging.info("Removing bad data based on QC rules")
            navexport.apply_qc()

        if parsed_args.type == 'bestres':
            logging.info("Building bestres dataset")
            navexport.build_bestres()
        elif parsed_args.type == '1min':
            logging.info("Building 1min dataset")
            navexport.build_1min()
        elif parsed_args.type == 'control':
            logging.info("Building control dataset")
            navexport.build_control()

        if parsed_args.outfile:
            logging.info("Saving nav export to %s in %s format" % (parsed_args.outfile, parsed_args.outfileformat))

            try:
                with open(parsed_args.outfile, 'w') as out_file:

                    if parsed_args.outfileformat == 'csv':
                        navexport.data.to_csv(out_file, index=False, na_rep='NAN', date_format='%Y-%m-%dT%H:%M:%S.%fZ')

                    elif parsed_args.outfileformat == 'geocsv':
                        out_file.write(navexport.geocsv_header(custom_meta))
                        navexport.data.to_csv(out_file, mode='a', index=False, na_rep='NAN', date_format='%Y-%m-%dT%H:%M:%S.%fZ')

            except IOError:
                logging.error("Error saving nav export file: %s", parsed_args.outfile)

        else:
            logging.info("Sending nav export to stdout in %s format" % parsed_args.outfileformat)

            if parsed_args.outfileformat == 'csv':
                output = StringIO()
                navexport.data.to_csv(output, index=False, na_rep='NAN', date_format='%Y-%m-%dT%H:%M:%S.%fZ')
                output.seek(0)
                print(output.read())

            elif parsed_args.outfileformat == 'geocsv':
                output = StringIO()
                navexport.data.to_csv(output, index=False, na_rep='NAN', date_format='%Y-%m-%dT%H:%M:%S.%fZ')
                output.seek(0)
                print(navexport.geocsv_header(custom_meta), end='')
                print(output.read())

    except KeyboardInterrupt:
        logging.warning('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)