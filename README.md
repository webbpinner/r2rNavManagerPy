# r2rNavManagerPy

## Overview
This project is a port of the offical PHP5/Java r2rNavManager project to Python3.  With PHP5 at end-of-life it made sense to port the very useful r2rNavManager to a modern/supported programming language.

## Repository Layout
- **bin** Contains the various r2rNavManagerPy programs
- **lib** Contains the common python classes and utility functions used in the r2rnavManagerPy programs
- **parsers** Contains the parser classes used by navparse.py to interpret the raw navigation files.
- **sample_data** Contains some sample data that can be used to 

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

    usage: navexport.py [-h] [-v] [-o outfile] [-O outfileformat] [-m [metadata ...]] [-q]
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
      -m [metadata ...], --meta [metadata ...]
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
    ```
    git clone https://github.com/webbpinner/r2rNavManagerPy.git
    ```
2. Create a virtual python environment within the repository
    ```
    cd ./r2rNavManagerPy
    python3 -m venv venv
    ```
3. Activate the virtual python environment
    ```
    source ./venv/bin/activate
    ```
5. Install the python packages required by r2rNavManagerPy
    ```
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip
    pip install wheel
    pip install -r ./requirements.txt 
    pip install --global-option=build_ext --global-option="-I/usr/include/gdal" GDAL==`gdal-config --version`
    ```
## Developing Parsers
In progress

## r2rnav file format

The tab-delimited r2rnav file format has been slightly changed from the original project.  The tab-delimited format has been replaced with a the comma-delimited format and optionally the files can be saved as a binary (HDF) format.  The advantage of the HDF format is faster loading by the r2rNavManagerPy utilities.

The updated format also includes serveral additional columns that provide additional information and improved QA/QC.  The additional columns are:
- **sensor_time**: the time from the sensor vs the time from the data acquisition system (DAS).  Strings like GGA include a satellite-caculated time of day.  Processing this field helps determine if there are any sequence errors in the data stream to the DAS.
- **deltaT**: the time difference between the previous row and the current row based on the timestamp added by the DAS.
- **sensor_deltaT**: the time difference between the previous row and the current row based on the timestamp added by the sensor.
- **valid_order**: returns 1 if the current row is newer than the previous row based on the deltaT and sensors_deltaT data.
- **distance**: the distance (in km) travelled between the previous row and the current row.
- **acceleration**: the acceleration (in m/s^2) between the previous row and the current row.

### Sample r2rnav format (csv-version):
```
iso_time,ship_longitude,ship_latitude,nmea_quality,nsv,hdop,antenna_height,valid_cksum,valid_parse,sensor_time,deltaT,sensor_deltaT,valid_order,distance,speed_made_good,course_made_good,acceleration
2019-03-19T13:13:02.854000Z,-118.976031,24.727157783333332,2,15,0.8,-25.495,1,1,1900-01-01T13:13:02.500000Z,0 days 00:00:00.500000,0 days 00:00:00.500000,1,0.0027703888882787907,5.540777776557581,114.8831731222835,
2019-03-19T13:13:03.368000Z,-118.97605585,24.727168466666665,2,15,0.8,-25.594,1,1,1900-01-01T13:13:03.000000Z,0 days 00:00:00.514000,0 days 00:00:00.500000,1,0.002776776016837137,5.553552033674274,115.32868856570866,0.024852640304849544
2019-03-19T13:13:03.836000Z,-118.97608061666666,24.727179033333332,2,15,0.8,-25.662,1,1,1900-01-01T13:13:03.500000Z,0 days 00:00:00.468000,0 days 00:00:00.500000,1,0.0027636303587799606,5.527260717559921,115.16024333496449,-0.05617802588536961
2019-03-19T13:13:04.351000Z,-118.97610543333333,24.727189616666667,2,15,0.8,-25.674,1,1,1900-01-01T13:13:04.000000Z,0 days 00:00:00.515000,0 days 00:00:00.500000,1,0.0027689889623471247,5.53797792469425,115.15052852676115,0.02081011094044444
2019-03-19T13:13:04.850000Z,-118.97613013333333,24.727200033333332,2,15,0.8,-25.667,1,1,1900-01-01T13:13:04.500000Z,0 days 00:00:00.499000,0 days 00:00:00.500000,1,0.0027504715041766067,5.500943008353214,114.9053946244768,-0.07421826922051336
2019-03-19T13:13:05.350000Z,-118.97615488333334,24.727210216666666,2,15,0.8,-25.598,1,1,1900-01-01T13:13:05.000000Z,0 days 00:00:00.500000,0 days 00:00:00.500000,1,0.002744245420962452,5.4884908419249046,114.36965936515116,-0.024904332856618083
2019-03-19T13:13:05.833000Z,-118.9761797,24.727220333333335,2,15,0.8,-25.518,1,1,1900-01-01T13:13:05.500000Z,0 days 00:00:00.483000,0 days 00:00:00.500000,1,0.0027473363778585612,5.494672755717122,114.17089489708633,0.012798993358628703

```

## Export Products

### bestres
The bestres data product contains the navigation data from a r2rnav file at the same resolution as the r2rnav file.  It can be generated as csv or as geocsv which includes the geocsv header record.  It can be generated with or without QC rules applied.  The bestres product includes the following columns:
- iso_time
- ship_longitude
- ship_latitude
- nmea_quality
- nsv
- hdop
- antenna_height
- speed_made_good
- course_made_good

#### Sample
```
#dataset: GeoCSV 2.0
#title: Processed Trackline Navigation Data: Best Resolution
#field_unit: ISO_8601,degree_east,degree_north,(unitless),(unitless),(unitless),meter,meter/second,degree
#field_type: datetime,float,float,integer,integer,float,float,float,float
#field_standard_name: iso_time,ship_longitude,ship_latitude,nmea_quality,nsv,hdop,antenna_height,speed_made_good,course_made_good
#field_long_name: date and time,longitude of vessel,latitude of vessel,NMEA quality indicator,number of satellite vehicles observed,horizontal dilution of precision,height of antenna above mean sea level,course made good,speed made good
#standard_name_cv: http://www.rvdata.us/voc/fieldname
#ellipsoid: WGS-84 (EPSG:4326)
#delimiter: ,
#field_missing: NAN
#attribution: Rolling Deck to Repository (R2R) Program; http://www.rvdata.us/
#source_repository: doi:10.17616/R39C8D
#source_event: doi:10.7284/908273
#source_dataset: doi:10.7284/133064
#cruise_id: FK190315
#creation_date: 2021-04-19T21:13:53Z
iso_time,ship_longitude,ship_latitude,nmea_quality,nsv,hdop,antenna_height,speed_made_good,course_made_good
2019-03-19T13:13:03.368000Z,-118.97605585,24.72716847,2,15,0.8,-25.594,NAN,NAN
2019-03-19T13:13:03.836000Z,-118.97608062,24.72717903,2,15,0.8,-25.662,5.53,115.16
2019-03-19T13:13:04.351000Z,-118.97610543,24.72718962,2,15,0.8,-25.674,5.54,115.151
2019-03-19T13:13:04.850000Z,-118.97613013,24.72720003,2,15,0.8,-25.667,5.5,114.905
```

### 1min
The 1min data product contains the navigation data from a r2rnav file at a one-min subsample.  It can be generated as csv or as geocsv which includes the geocsv header record.  It can be generated with or without QC rules applied.  The 1min product includes the following columns:
- iso_time
- ship_longitude
- ship_latitude
- speed_made_good
- course_made_good

#### Sample
```
#dataset: GeoCSV 2.0
#title: Processed Trackline Navigation Data: One Minute Resolution
#field_unit: ISO_8601,degree_east,degree_north,meter/second,degree
#field_type: datetime,float,float,float,float
#field_standard_name: iso_time,ship_longitude,ship_latitude,speed_made_good,course_made_good
#field_long_name: date and time,longitude of vessel,latitude of vessel,speed made good,course made good
#standard_name_cv: http://www.rvdata.us/voc/fieldname
#ellipsoid: WGS-84 (EPSG:4326)
#delimiter: ,
#field_missing: NAN
#attribution: Rolling Deck to Repository (R2R) Program; http://www.rvdata.us/
#source_repository: doi:10.17616/R39C8D
#source_event: doi:10.7284/908273
#source_dataset: doi:10.7284/133064
#cruise_id: FK190315
#creation_date: 2021-04-19T20:38:10Z
iso_time,ship_longitude,ship_latitude,speed_made_good,course_made_good
2019-03-19T13:13:00.000000Z,-118.97605585,24.72716847,NAN,NAN
2019-03-19T13:14:00.000000Z,-118.97892645,24.72830543,5.27,113.559
2019-03-19T13:15:00.000000Z,-118.98193595,24.72951233,5.54,113.822
2019-03-19T13:16:00.000000Z,-118.98493005,24.73074472,5.53,114.378
```

### control
The control data product contains the navigation data from a r2rnav file but has been reduced using the Ramer–Douglas–Peucker algorithm (epsilon = 0.001).  It can be generated as csv or as geocsv which includes the geocsv header record.  It can be generated with or without QC rules applied.  The control product includes the following columns:
- iso_time
- ship_longitude
- ship_latitude

#### Sample
```
#dataset: GeoCSV 2.0
#title: Processed Trackline Navigation Data: Control Points
#field_unit: ISO_8601,degree_east,degree_north
#field_type: datetime,float,float
#field_standard_name: iso_time,ship_longitude,ship_latitude
#field_long_name: date and time,longitude of vessel,latitude of vessel
#standard_name_cv: http://www.rvdata.us/voc/fieldname
#ellipsoid: WGS-84 (EPSG:4326)
#delimiter: ,
#field_missing: NAN
#attribution: Rolling Deck to Repository (R2R) Program; http://www.rvdata.us/
#source_repository: doi:10.17616/R39C8D
#source_event: doi:10.7284/908273
#source_dataset: doi:10.7284/133064
#cruise_id: FK190315
#creation_date: 2021-04-19T21:01:21Z
iso_time,ship_longitude,ship_latitude
2019-03-19T13:13:03.368000Z,-118.97605585,24.72716847
2019-03-19T14:56:57.342000Z,-119.28450778,24.8488401
2019-03-19T15:23:06.851000Z,-119.34884445,24.87714828
2019-03-19T15:24:20.343000Z,-119.34978913,24.87956312
```

## Typical Workflow Using Sample data
This section describes howto process the sample data included with the repository to produce the standard suite of r2rNavManager products.

1. Go to the repo dirctory:
```
cd ~/r2rNavManagerPy
```

2. Make a directory for the output:
```
mkdir ./sample_output
```

3. Use navparse.py to parse the sample data files into a r2rnav formatted file:
```
./venv/bin/python ./bin/navparse.py -v -f nav02 -o ./sample_output/sample_data.r2rnav ./sample_data/COM18*.Raw 
```

4. Use navinfo to display the temporal and geographic bounds for the r2rnav file:
```
./venv/bin/python ./bin/navinfo.py -v ./sample_output/sample_data.r2rnav
```

5. Use navqa to display the quality assurance report for the r2rnav file:
```
./venv/bin/python ./bin/navqa.py -v ./sample_output/sample_data.r2rnav
```

5. Use navexport to build the various r2r nav products from the r2rnav file:
```
./venv/bin/python ./bin/navexport.py -v -q --meta cruise_id=FK190315 -o ./sample_output/FK190315_bestres.geocsv ./sample_output/sample_data.r2rnav
./venv/bin/python ./bin/navexport.py -v -q --meta cruise_id=FK190315 -t 1min -o ./sample_output/FK190315_1min.geocsv ./sample_output/sample_data.r2rnav
./venv/bin/python ./bin/navexport.py -v -q --meta cruise_id=FK190315 -t control -o ./sample_output/FK190315_control.geocsv ./sample_output/sample_data.r2rnav
```
