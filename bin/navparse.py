#!/usr/bin/env python3
# ----------------------------------------------------------------------------------- #
#
#         FILE:  navparse.py
#
#  DESCRIPTION:  Parse raw position data, process and export into r2rnav intermediate
#                format.
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

import argparse
import os
import sys
import json
import glob
import logging
import pandas as pd
from io import StringIO
from datetime import datetime

from os.path import dirname, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

from lib.utils import build_file_list, is_valid_nav_format
from lib.nav_manager import NavFileReport
from parsers.nav02_parser import Nav02Parser
from parsers.nav33_parser import Nav33Parser

def check_nav_format(nav_format):
    if is_valid_nav_format(nav_format):
        return nav_format
    else:
        raise argparse.ArgumentTypeError("%s is an invalid nav format" % nav_format)

# -------------------------------------------------------------------------------------
# Required python code for running the script as a stand-alone utility
# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse raw position data, process and export into r2rnav intermediate format')
    parser.add_argument('-v', '--verbosity', dest='verbosity', default=0, action='count', help='Increase output verbosity, default level: warning')
    parser.add_argument('-f', '--format', type=check_nav_format, metavar='format', required=True, help='Format type of input file(s)')
    parser.add_argument('-l', '--logfile', type=str, metavar='logfile', help='Write file report to specified logfile')
    parser.add_argument('-L', '--logfileformat', type=str, default="text", choices=["text","json"], metavar='logfileformat', help='The file report format: text or json, default: text')
    parser.add_argument('-o', '--outfile', type=str, metavar='outfile', help='Write output to specified outfile')
    parser.add_argument('-O', '--outfileformat', type=str, metavar='outfileformat', default="csv", choices=["csv","hdf"], help='The outfile format: csv or hdf, default: csv')
    parser.add_argument('--startTS', type=lambda d: datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%fZ'), metavar='startTS', help='Crop data to start timestamp, format: YYYY-mm-ddTHH:MM:SS.sssZ')
    parser.add_argument('--endTS', type=lambda d: datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%fZ'), metavar='endTS', help='Crop data to end timestamp, format: YYYY-mm-ddTHH:MM:SS.sssZ')
    parser.add_argument('input', type=str, nargs='*', help='The input files, directories and/or file globs')

    parsed_args = parser.parse_args()

    ############################
    # Set up logging before we do any other argument parsing (so that we
    # can log problems with argument parsing).
  
    LOGGING_FORMAT = '%(asctime)-15s %(levelname)s - %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT)

    LOG_LEVELS = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
    parsed_args.verbosity = min(parsed_args.verbosity, max(LOG_LEVELS))
    logging.getLogger().setLevel(LOG_LEVELS[parsed_args.verbosity])

    # Set file parser
    nav_parser = None

    if(parsed_args.format == 'nav02'):
        nav_parser = Nav02Parser()
    elif(parsed_args.format == 'nav33'):
        nav_parser = Nav33Parser()

    # Display information about parser
    logging.info("Parser Name: %s" % nav_parser.name)
    logging.info("Parser Description: %s" % nav_parser.description)
    logging.info("Parser Example Data: %s\n  " % "\n  ".join(nav_parser.example_data.split("\n")).rstrip())

    # Build filelist
    fileList = build_file_list(parsed_args.input)

    logging.info('Input files:\n  %s' % '\n  '.join(fileList))
    if parsed_args.outfile:
        logging.info('Outfile: %s' % parsed_args.outfile)

    # If there are no files to process then quit
    if not fileList:
        logging.error("No files to process")
        sys.exit(0)

    # Process the files
    try:
        for file in fileList:
            logging.info("Parsing data file: %s" % file)

            results, parse_errors = nav_parser.parse_file(file)

            if results is None:
                logging.warning("Problem parsing file: %s" % file)
                sys.exit(0)

            # If no data ingested from file, quit
            if len(results['iso_time']) == 0:
                logging.warning("No usable data parsed.")
                continue

            df = pd.DataFrame(results)

            # Set lines with parsing errors
            fileReport = NavFileReport(file)
            fileReport.build_report(df, parse_errors)

            nav_parser.add_file_report(fileReport)

            # Build DataFrame
            logging.debug("Building dataframe from parsed data...")
            nav_parser.add_dateframe(df)

        if parsed_args.startTS:
            logging.info("Cropping data older than %s" % parsed_args.startTS.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
            nav_parser.crop_dataframe(start = parsed_args.startTS)

        if parsed_args.endTS:
            logging.info("Cropping data newer than %s" % parsed_args.endTS.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
            nav_parser.crop_dataframe(end = parsed_args.endTS)

        if nav_parser.dataframe.shape[0] == 0:
            logging.warning("Data is empty after cropping for start/end timestamps")

        else:
            logging.info("Processing data")
            nav_parser.proc_dataframe()

        logging.info("File report(s):\n%s" % '\n'.join([str(report) for report in nav_parser.file_report]))

        if parsed_args.logfile:
            logging.info("Saving file report to %s in %s format" % (parsed_args.logfile, parsed_args.logfileformat))

            try:
                with open(parsed_args.logfile, 'w') as report_file:
                    logging.debug("Saving file report file: %s", parsed_args.logfile)

                    if parsed_args.logfileformat == 'json':
                        json.dump([report.to_json() for report in nav_parser.file_report], report_file, indent=2)

                    elif parsed_args.logfileformat == 'text':
                        report_file.write('\n\n'.join([str(report) for report in nav_parser.file_report]))

            except IOError:
                logging.error("Error saving file report file: %s", parsed_args.logfile)

        if parsed_args.outfile:
            logging.info("Saving data to %s in %s format" % (parsed_args.outfile, parsed_args.outfileformat))

            if parsed_args.outfileformat == 'csv':
    
                try:
                    with open(parsed_args.outfile, 'w') as data_file:
                        nav_parser.dataframe.to_csv(data_file, index=False, date_format='%Y-%m-%dT%H:%M:%S.%fZ')

                except IOError:
                    logging.error("Error saving data file: %s", parsed_args.outfile)

            elif parsed_args.outfileformat == 'hdf':

                try:
                    with pd.HDFStore(parsed_args.outfile) as data_file:
                        data_file.put(key="nav_data", value=nav_parser.dataframe, format='table', data_columns=True)

                except IOError:
                    logging.error("Error saving data file: %s", parsed_args.outfile)


        else:
            logging.info("Send data to stdout in csv format")
            output = StringIO()
            nav_parser.dataframe.to_csv(output, index=False, date_format='%Y-%m-%dT%H:%M:%S.%fZ')
            output.seek(0)
            print(output.read())

        # logging.info("Datatypes:\n%s" % nav_parser.dataframe.dtypes)

        # logging.info(nav_parser.dataframe)


    except KeyboardInterrupt:
        logging.warning('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)