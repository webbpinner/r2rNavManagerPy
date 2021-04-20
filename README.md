# r2rNavManagerPy

## Overview
This project is a Python3 port of the offical php5/Java r2rNavManager project.  With PHP5 at end-of-life it makes sense to port the very useful r2rNavManager to a more modern programming language.

## Repository Layout
- bin Contains the various r2rNavManagerPy programs
- lib Contains the common python classes and utility functions used in the r2rnavManagerPy programs
- parsers Contains the parser classes used by navparse.py to interpret the raw navigation files.
- sample_data Contains some sample data that can be used to 

## Tools
### navparse.py
navparse.py parses the raw navigation files and produces a common r2rnav file format.

    usage: navparse.py [-h] [-v] -f format [-l logfile] [-L logfileformat] [-o outfile] [-O outfileformat]
                       [--startTS startTS] [--endTS endTS] [input ...]

    Parse raw position data, process and export into r2rnav intermediate format

    positional arguments:
      input                 The input files, directories and/or file globs

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbosity       Increase output verbosity, default level: warning
      -f format, --format format
                            Format type of input file(s)
      -l logfile, --logfile logfile
                            Write file report to specified logfile
      -L logfileformat, --logfileformat logfileformat
                            The file report format: text or json, default: text
      -o outfile, --outfile outfile
                            Write output to specified outfile
      -O outfileformat, --outfileformat outfileformat
                            The outfile format: csv or hdf, default: csv
      --startTS startTS     Crop data to start timestamp, format: YYYY-mm-ddTHH:MM:SS.sssZ
      --endTS endTS         Crop data to end timestamp, format: YYYY-mm-ddTHH:MM:SS.sssZ

### navinfo.py
navinfo.py creates a brief report from a r2rnav file that shows start/end times and positions as well as the geographic bounding box.

    usage: navinfo.py [-h] [-v] [-l outfile] [-L logfileformat] [--startTS startTS] [--endTS endTS]
                      [-I inputformat] input

    Return information based on r2rnav formatted file

    positional arguments:
      input                 The input r2rnav file

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbosity       Increase output verbosity, default level: warning
      -l outfile, --logfile outfile
                            Write output to specified logfile
      -L logfileformat, --logfileformat logfileformat
                            The format of the logfile, text, json, default: text
      --startTS startTS     Crop data to start timestamp, format: YYYY-mm-ddTHH:MM:SS.sssZ
      --endTS endTS         Crop data to end timestamp, format: YYYY-mm-ddTHH:MM:SS.sssZ
      -I inputformat, --inputformat inputformat
                            The format type of input file, csv, hdf, default: csv
                            
### navqa.py
navqa.py create a quality assurance report from a r2rnav file that shows the various QA statisics for the data set.

    usage: navqa.py [-h] [-v] [-l logfile] [-L logfileformat] [--startTS startTS] [--endTS endTS]
                    [-g gapthreshold] [-s speedthreshold] [-a accelerationthreshold] [-I inputformat]
                    input

    Return quality assurance information based on r2rnav formatted file

    positional arguments:
      input                 The input r2rnav file

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbosity       Increase output verbosity, default level: warning
      -l logfile, --logfile logfile
                            Write output to specified logfile
      -L logfileformat, --logfileformat logfileformat
                            The format of the logfile: text, json, default: text
      --startTS startTS     Crop data to start timestamp, format: YYYY-mm-ddTHH:MM:SS.sssZ
      --endTS endTS         Crop data to end timestamp, format: YYYY-mm-ddTHH:MM:SS.sssZ
      -g gapthreshold, --gapthreshold gapthreshold
                            Set custom gap threshold in seconds
      -s speedthreshold, --speedthreshold speedthreshold
                            Set custom speed threshold in m/s
      -a accelerationthreshold, --accelerationthreshold accelerationthreshold
                            Set custom acceleration threshold in m/s^2
      -I inputformat, --inputformat inputformat
                            The format type of input file: csv, hdf, default: csv
### navexport.py
navexport.py creates the various r2rNavManager products from a r2rnav file such as bestres, 1min, and control.

    usage: navexport.py [-h] [-v] [-o outfile] [-O outfileformat] [-m [metadatafile ...]] [-q]
                        [-t outputtype] [--startTS startTS] [--endTS endTS] [-g gapthreshold]
                        [-s speedthreshold] [-a accelerationthreshold] [-I inputformat] input

    Export r2r nav products based on r2rnav formatted file

    positional arguments:
      input                 The input r2rnav file

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbosity       Increase output verbosity, default level: warning
      -o outfile, --outfile outfile
                            Write output to specified outfile
      -O outfileformat, --outfileformat outfileformat
                            The outfile format: csv or geocsv, default: geocsv
      -m [metadatafile ...], --meta [metadatafile ...]
                            Add custom metadata to the geocsv header, overrides default vaules, format: "key=value"
      -q, --qc              Exclude bad data points before exporting data
      -t outputtype, --type outputtype
                           The type of output to generate: bestres, 1min, control, default: bestres
      --startTS startTS     Crop data to start timestamp, format: YYYY-mm-ddTHH:MM:SS.sssZ
      --endTS endTS         Crop data to end timestamp, format: YYYY-mm-ddTHH:MM:SS.sssZ
      -g gapthreshold, --gapthreshold gapthreshold
                            Set custom gap threshold in seconds
      -s speedthreshold, --speedthreshold speedthreshold
                            Set custom speed threshold in m/s
      -a accelerationthreshold, --accelerationthreshold accelerationthreshold
                            Set custom acceleration threshold in m/s^2
      -I inputformat, --inputformat inputformat
                            The format type of input r2rnav file: csv, hdf, default: csv             
## Install
### Requirements:
- Python >=3.8

### Instructions
1. Clone the repository to the local machine
2. Create a virtual python environment within the repository
3. Activate the virtual python environment
4. Install the python packages required by r2rNavManagerPy

## Developing Parsers

## r2rnav file format.

## Export Products

### bestres

### 1min

### control
