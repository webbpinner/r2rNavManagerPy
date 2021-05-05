#!/usr/bin/env python3
'''
        FILE:  geojson_templates.py
 DESCRIPTION:  contains the geoCSV formatted header templates for the various
               r2rNavManagerPy geoCSV products

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

bestres_header = {
    'dataset': 'GeoCSV 2.0',
    'title': 'Processed Trackline Navigation Data: Best Resolution',
    'field_unit': 'ISO_8601,degree_east,degree_north,(unitless),(unitless),(unitless),meter,meter/second,degree',
    'field_type': 'datetime,float,float,integer,integer,float,float,float,float',
    'field_standard_name': 'iso_time,ship_longitude,ship_latitude,nmea_quality,nsv,hdop,antenna_height,speed_made_good,course_made_good',
    'field_long_name': 'date and time,longitude of vessel,latitude of vessel,NMEA quality indicator,number of satellite vehicles observed,horizontal dilution of precision,height of antenna above mean sea level,course made good,speed made good',
    'standard_name_cv': 'http://www.rvdata.us/voc/fieldname',
    'ellipsoid': 'WGS-84 (EPSG:4326)',
    'delimiter': ',',
    'field_missing': 'NAN',
    'attribution': 'Rolling Deck to Repository (R2R) Program; http://www.rvdata.us/',
    'source_repository': 'doi:10.17616/R39C8D',
    'source_event': 'doi:10.7284/908273',
    'source_dataset': 'doi:10.7284/133064',
    'cruise_id': '',
    'creation_date': ''
}

onemin_header = {
    'dataset': 'GeoCSV 2.0',
    'title': 'Processed Trackline Navigation Data: One Minute Resolution',
    'field_unit': 'ISO_8601,degree_east,degree_north,meter/second,degree',
    'field_type': 'datetime,float,float,float,float',
    'field_standard_name': 'iso_time,ship_longitude,ship_latitude,speed_made_good,course_made_good',
    'field_long_name': 'date and time,longitude of vessel,latitude of vessel,speed made good,course made good',
    'standard_name_cv': 'http://www.rvdata.us/voc/fieldname',
    'ellipsoid': 'WGS-84 (EPSG:4326)',
    'delimiter': ',',
    'field_missing': 'NAN',
    'attribution': 'Rolling Deck to Repository (R2R) Program; http://www.rvdata.us/',
    'source_repository': 'doi:10.17616/R39C8D',
    'source_event': 'doi:10.7284/908273',
    'source_dataset': 'doi:10.7284/133064',
    'cruise_id': '',
    'creation_date': '',
}

control_header = {
    'dataset': 'GeoCSV 2.0',
    'title': 'Processed Trackline Navigation Data: Control Points',
    'field_unit': 'ISO_8601,degree_east,degree_north',
    'field_type': 'datetime,float,float',
    'field_standard_name': 'iso_time,ship_longitude,ship_latitude',
    'field_long_name': 'date and time,longitude of vessel,latitude of vessel',
    'standard_name_cv': 'http://www.rvdata.us/voc/fieldname',
    'ellipsoid': 'WGS-84 (EPSG:4326)',
    'delimiter': ',',
    'field_missing': 'NAN',
    'attribution': 'Rolling Deck to Repository (R2R) Program; http://www.rvdata.us/',
    'source_repository': 'doi:10.17616/R39C8D',
    'source_event': 'doi:10.7284/908273',
    'source_dataset': 'doi:10.7284/133064',
    'cruise_id': '',
    'creation_date': '',
}
