#!/usr/bin/python

"""
Turn a shapefile into csv. Requires GDAL with python bindings
"""
import sys
import argparse
import json
import uuid
import ogr

parser = argparse.ArgumentParser()
parser.add_argument("shp", help="path to shapefile")
parser.add_argument("-i", "--info", type=bool, help="Show layers info in ShapeFile. When used with '-l' shows info about layer", default=False)
parser.add_argument("-l", "--layer", type=str, help="The layer to use.")
parser.add_argument("-k", "--key", type=str, help="The Field to use as a Unique Key When Converting to json. This is how Features are labeled.")

args = parser.parse_args()

def get_shp(path_to_shp):
    ds = ogr.Open(args.shp)
    if ds is None:
        print "Could not open shape file: '%s'" % path_to_shp
        sys.exit(1)

    return ds

def get_layer(ds, layer_name):
    lyr = ds.GetLayerByName(layer_name)
    if lyr == None:
        print "No layer '%s'" % layer_name
        sys.exit(1)
    return lyr

def show_layer_names(ds):
    """ Show list of layers and thier indexes in the datasource <ds>"""
    lyr_count = ds.GetLayerCount()
    print "Total Layers: %s" % lyr_count
    for i in range(lyr_count):
        lyr = ds.GetLayerByIndex(i)
        print "%s)" % i, "Name: %s" % lyr.GetName()
    sys.exit(0)

def get_layer_fields(lyr):
    """ Return lyr fields """
    fields = []
    defn = lyr.GetLayerDefn()
    for i in range(defn.GetFieldCount()):
        fields.append(defn.GetFieldDefn(i))
    return fields

def show_layer_info(ds, layer_name):
    lyr = get_layer(ds, layer_name)
    print "------------------------------ %s -------------------------------------" % layer_name
    print "Geom Type: %s" % lyr.GetGeomType()
    print "Total Features: %s"  % lyr.GetFeatureCount()
    print "Fields: %s" % ", ".join([l.GetName() for l in get_layer_fields(lyr)])
    sys.exit(0)

def iter_layer_features(lyr, field_key):
    """ Returns a dict representation of the layer
        <field_key> is a key to use as a Unique Identifier
    """
    fields = get_layer_fields(lyr)
    layers = {}
    if field_key not in [f.GetName() for f in fields]:
        print "Please Specify a Field to use as a Key"
        sys.exit(1)

    for ftr in lyr:
        key = ftr.GetFieldAsString(field_key).strip()
        #incase key is an empty string, we'll stick in a uuid
        if key == "":
            key = str(uuid.uuid4())
        layers[key] = {}
        field_vals = {}

        for f in fields:
            f_name = f.GetName()
            field_val = ftr.GetFieldAsString(f_name)
            field_vals[f_name] = field_val
        geom = ftr.GetGeometryRef()
        geo_dict = json.loads(geom.ExportToJson())

        layers[key]['fields'] = field_vals
        layers[key]['geom'] = geo_dict

    return layers

def main():
    ds = get_shp(args.shp)
    if args.info and not args.layer:
        show_layer_names(ds)
    elif args.info and args.layer:
        show_layer_info(ds, args.layer)
    # if we havent exited by now we need to start doing some real work
    if args.layer:
        lyr = get_layer(ds, args.layer)
        print json.dumps(iter_layer_features(lyr, args.key))


if __name__ == '__main__':

    main()


