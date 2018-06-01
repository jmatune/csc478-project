import json
import urllib3
import re
from shapely.geometry import Polygon, Point
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

def get_name(lat, long):
    point_tuple = Point(float(lat)*-1, float(long))
    n_name = 'Not Found'
    for key_name in poly_dict.keys():
        n_poly = poly_dict[key_name]

        if point_tuple.within(n_poly):
            n_name = key_name
    return n_name


#  create shapely polygons from json coordinate strings
poly_dict = {}
for item in raw_dict['data']:
    neighborhood, poly = get_poly(item)
    shapely_poly = Polygon(poly)
    poly_dict[neighborhood] = shapely_poly

#  read in school data
hs_data = pd.read_csv('school_lib.csv', sep=',', header=0)
hs_data['Neighborhood Name'] = 'None'

for row in range(hs_data.shape[0]):
    hs_data['Neighborhood Name'].iloc[row] = get_name(hs_data['School_Longitude.1'].iloc[row], hs_data['School_Latitude.1'].iloc[row])

#  Read in census data for non-english language
census_lang = pd.read_csv('Census_Neighborhood_Language.csv', sep=',', header=0)
census_lang.set_index(['NEIGHBORHOOD'], inplace=True)

#  join to school data
hs_data_lang = hs_data.join(census_lang, on='Neighborhood Name')

census_econ = pd.read_csv('Census_Socio_Econ.csv', sep=',', header=0)
census_econ.set_index(['NEIGHBORHOOD'], inplace=True)
print census_econ.head(10)
#  join to school data
hs_data_lang_socio = hs_data_lang.join(census_econ, on='Neighborhood Name')

print hs_data_lang_socio
