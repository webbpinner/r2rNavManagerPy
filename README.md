# r2rNavManagerPy

## Overview
This project is a Python3 port of the offical php5/Java r2rNavManager project.  With PHP5 at end-of-life it makes sense to port the very useful r2rNavManager to a more modern programming language.

## Repository Layout
- bin
- lib
- parsers
- sample_data

## Tools
### navparse.py
navparse.py parses the raw position files and produces a common r2rnav file format.

    usage: navparse.py [-h] [-v] -f format [-l logfile] [-L logfileformat] [-o outfile] [-O outfileformat] [--startTS startTS] [--endTS endTS] [input ...]

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

### navqa.py
navqa.py create a quality assurance report from a r2rnav file that shows the various QA statisics for the data set.

### navexport.py
navexport.py creates the various r2rNavManager products from a r2rnav file such as bestres, 1min, and control.

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
