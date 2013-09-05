# Some Tools for working with Geo Things

## shp_to_json.py
Convert a shapefile layer to json. Requires gdal - ogr to be installed properly. Use apt-get!

### Usage
```
shp_to_json.py [-h] [-i INFO] [-l LAYER] [-k KEY] shp

positional arguments:
shp                   path to shapefile
  
optional arguments:
-h, --help            show this help message and exit
-i INFO, --info INFO  Show layers info in ShapeFile.
-l LAYER, --layer LAYER The layer to use, If combined with -i you'll get info about that layer
-k KEY, --key KEY     The Field to use as a Unique Key when creating final output
                               
```
### Examples
```
Get the list of layers
    $ ./shp_to_json.py ~/Desktop/shapefiles/tract2010_raw_bic.shp -i t
    # outputs 
    Total Layers: 1
    0) Name: tract2010_raw_bic

Get Info about that layer
    $ ./shp_to_json.py ~/Desktop/shapefiles/tract2010_raw_bic.shp -i t -l tract2010_raw_bic
    # outputs
    ------------------------------ tract2010_raw_bic -------------------------------------
    Geom Type: 3
    Total Features: 241
    Fields: STATEFP10, COUNTYFP10, TRACTCE10, GEOID10, NAME10, NAMELSAD10, MTFCC10, FUNCSTAT10, ALAND10, AWATER10, INTPTLAT10, INTPTLON10, MUNI


Export it to json using NAME10 as the Key
    $ ./shp_to_json.py ~/Desktop/shapefiles/tract2010_raw_bic.shp -l tract2010_raw_bic -k NAME10 > output.json
```


### SampleOutput
    {
    "1": {
        "fields": {
            "id": "1"
        },
        "geom": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-1.60121647819063, 0.12589337641357],
                    [-1.962525040387722, 0.292129240710824],
                    [-1.962525040387722, 0.292129240710824],
                    [-1.706386106623586, 0.309092084006462],
                    [-1.611394184168013, 0.298914378029079],
                    [-0.814140549273021, 0.329447495961227],
                    [-0.692008077544426, -0.301570274636511],
                    [-0.919310177705977, -0.01659450726979],
                    [-1.102508885298869, -0.318533117932149],
                    [-1.231426494345719, -0.606901453957997],
                    [-1.665675282714055, -0.701893376413571],
                    [-1.838696284329564, -0.382991922455574],
                    [-1.960828756058158, -0.142119547657513],
                    [-1.60121647819063, 0.12589337641357]
                ]
            ]
        }
    }
    }

