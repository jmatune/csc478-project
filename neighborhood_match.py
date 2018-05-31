import json
import urllib3
import re
from shapely.geometry import Polygon
import pandas as pd

pool = urllib3.PoolManager()
# Open URL and consume json
source = pool.request('GET', 'https://data.cityofchicago.org/api/views/igwz-8jzy/rows.json')
raw_lines = source.data
raw_dict = json.loads(raw_lines)

# JSON is structured with two main sections: 'meta' and 'data'
# All geo boundaries are stored within 'data' section, which is a list of lists, with one entry per neighborhood
# Coordinates are stored starting at 9th entry (counting from 1). Community name is 4th from end.

# Goal is to iterate through list entries and return the name with coordinates as list of tuples (shapely format)


# Take list entry for neighborhood
# Return neighborhood name and shapely poly object
def get_poly(geo_list):
    # Retrieve name
    name = geo_list[len(geo_list)-4]

    # Retrieve coordinate tuples
    geo_string = geo_list[8]
    coord_string = geo_string[16:len(geo_string)-3]  # strips unnecessary junk at head and tail
    poly_tuples = list([list(map(str, coords.lstrip().split(' '))) for coords in coord_string.split(',')])

    #  define regex string to parse out non-numeric characters
    non_decimal = re.compile(r'[^\d.]+')

    #  loop through coordinate pairs to remove problem characters, then transform to tuple
    for n, poly_tup in enumerate(poly_tuples):
        for i, value in enumerate(poly_tup):
            poly_tup[i] = float(non_decimal.sub('', value))
        poly_tuples[n] = tuple(poly_tuples[n])
    return name, poly_tuples

#  create shapely polygons from json coordinate strings
poly_dict = {}
for item in raw_dict['data']:
    neighborhood, poly = get_poly(item)
    shapely_poly = Polygon(poly)
    poly_dict[neighborhood] = shapely_poly

#  read in school data
hs_data = pd.read_csv('CPS_HS_Progress_Report_1314.txt', sep='\t', header=0)
print(hs_data.head())

