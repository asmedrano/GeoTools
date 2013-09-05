#!/usr/bin/python
import sys
import hashlib
import json
import geohash
from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily

def get_connection(keyspace='Keyspace1', hosts=['localhost:9160']):
    pool = ConnectionPool(keyspace, hosts) # default connection
    col_fam = ColumnFamily(pool, 'GeographyFam1')
    index_col = ColumnFamily(pool, 'GeographyMeta1') # super Column
    return col_fam, index_col


def open_file(file_path):
    geo_dict = None
    try:
        with open(file_path) as f:
            geo_dict = json.loads(f.read())
    except IOError:
        pass
    return geo_dict

def gen_hash(string):
    return hashlib.md5(string).digest().encode("base64")

def insert_feature_index(col_fam, src_name, feature_count,  feature_key):
    """ We maintain an index of each feature that is imported with each shapefile we import. Super Columns are used"""
    feat_key = "feat_%s" % feature_count
    feat_dict = {}
    feat_dict[feat_key] = {'key': feature_key,
                           'geom':gen_hash(src_name+feature_key+"geom"),
                           'meta':gen_hash(src_name+feature_key+"meta")}
    col_fam.insert(src_name, feat_dict)
    return col_fam.get(src_name)

def create_fields_meta_cols(col_fam, src_name, feature_key, fields):
    """ Insert all fields into the meta column for this key
        These are all meta rows and they are going into row that may already exist.
        The Row Key is always a hash of the src_name + feature_key + meta
    """
    row_key = gen_hash(src_name + feature_key + "meta")
    col_fam.insert(row_key, fields)
    return col_fam.get(row_key)

def create_geom_rows(col_fam, src_name, feature_key, geom_dict):
    """ Insert geometry rows for each feature in very wide cols
        Row key is scr_name + feature_key
        Each lat long is geohashed
    """
    row_key = hash(src_name + feature_key + "geom")
    geom_type = geom_dict['type']

    if geom_type == "Polygon":
        coords = geom_dict['coordinates'][0]

    c_count = 0 # keeping track of cords count for column names
    cols = {'type':geom_type}

    for c in coords:
        c_count += 1
        g_h = geohash.encode(c[0], c[1])
        cols["p_%s" % c_count] = g_h

    col_fam.insert(row_key, cols)
    return col_fam.get(row_key)

def import_geo(col_fam, idx_col, shp_dict, src_name):
    """ Actually import the shp_dict into cassandra"""
    feature_count = 0 # keep count of features
    for feature_key in shp_dict.iterkeys():
        feature_count += 1
        idx = insert_feature_index(idx_col, src_name, feature_count, feature_key)
        fields = create_fields_meta_cols(col_fam, src_name, feature_key, shp_dict[feature_key]['fields'])
        geoms = create_geom_rows(col_fam, src_name, feature_key, shp_dict[feature_key]['geom'])
        print geoms

def main(file_name):
    col_fam, idx_col = get_connection()
    geo_data = open_file(file_name)
    if geo_data == None:
        exit_p("Couldnt open file '%s'." % file_name, 1)

    import_geo(col_fam, idx_col, geo_data, file_name)

def exit_p(mssg, status):
    print mssg
    exit(status)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit_p("Please specify a json file to use.", 1)

    geojson_file = sys.argv[1]

    main(geojson_file)
