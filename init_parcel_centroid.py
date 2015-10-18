#!./YOUR_ENV_NAME/bin/python
"""
Given a parcel lines shapefile downloaded from
http://www.mcauditor.org/downloads/gis_download_shape.cfm,

that has been converted from Lambert_Conformal_Conic to D_WGS_1984 via
the following command:

ogr2ogr -t_srs EPSG:4326 out.shp in.shp

this Python script creates a centroids.dbm file that contains the following
(key,value) pairs:
    key: Shapefile record 'taxpinno'
    value: Shapefile shape bounding box centroid (latitude, longitude)"""
import dbm
import numpy as np
import re
import shapefile
import sys

def initialize_record(fields,\
                      shape_record):
    """Initializes a dictionary that stores a shapefile record.

    Args:
        fields: List that stores the shapefile record names

        shape_record: Object that contains a shapefile record
                      and associated shape

    Returns:
        record: Dictionary that stores a shapefile record."""
    record = {}

    for idx in range(0, len(fields)):
        record[fields[idx]] = shape_record.record[idx]

        if isinstance(record[fields[idx]], basestring):
            record[fields[idx]] =\
                re.sub("\\s+", " ", record[fields[idx]])

    return record

def is_government(name):
    """Returns a boolean that keeps track of whether or not a shapefile record
    is associated with a local, county, or state government.

    Args:
        name: String that stores a shapefile record name

    Returns:
        is_government_flag: Boolean that keeps track of whether or not a
                            shapefile record is associated with a local
                            county, or state government."""

    is_government_flag = False

    government_regex = ['^city of dayton.*$',\
                        '^board of county commissioners$',\
                        '^dayton mont co public$',\
                        '^dayton, city of$',\
                        '^miami conservancy district$',\
                        '^state of ohio.*$']

    for regex in government_regex:
        is_government_flag =\
            is_government_flag | (re.match(regex, name) != None)

    return is_government_flag

def init_parcel_centroid(argv):
    """Given a parcel lines shapefile downloaded from
    http://www.mcauditor.org/downloads/gis_download_shape.cfm,

    that has been converted from Lambert_Conformal_Conic to D_WGS_1984 via
    the following command:

    ogr2ogr -t_srs EPSG:4326 out.shp in.shp

    this Python script creates a centroids.dbm file that contains the
    following (key,value) pairs:

    key: Shapefile record 'taxpinno'
    value: Shapefile shape bounding box centroid (latitude, longitude)

    Args:
        argv: List that stores command line arguments

              Index:   Description:
              -----    -----------
                0      Python script name

                1      Parcel lines shapefile basename

    Returns:
        None"""
    shapefileobj = shapefile.Reader(argv[1])

    fields = [re.sub("_", "", field[0].lower())\
              for field in shapefileobj.fields[1:]]

    centroids = dbm.open("centroids.dbm", "c")

    for shape_record in shapefileobj.shapeRecords():
        record = initialize_record(fields,\
                                   shape_record)
        try:
          record['name'] = record['name'].lower()
        except:
          print record['taxpinno']

        if re.match('^R72$', record['taxdistric']):
            try:
              if not is_government(record['name']):
                  bbox = np.array(shape_record.shape.bbox)

                  centroids[record['taxpinno']] =\
                      "%f %f" % (np.mean(bbox[1:4:2]),\
                                 np.mean(bbox[0:4:2]))
            except:
              bbox = np.array(shape_record.shape.bbox)

              centroids[record['taxpinno']] =\
                  "%f %f" % (np.mean(bbox[1:4:2]),\
                             np.mean(bbox[0:4:2]))

    centroids.close()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        init_parcel_centroid(sys.argv)
    else:
        print "Usage: init_parcel_centroid.py " +\
              "<parcellines shapefile basename>"

