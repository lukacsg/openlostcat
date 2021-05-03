"""
ask_osm is about querying OpenStreetMap using the Overpass API
"""

import requests

# overpass_url : the API address
# for other examples see the page: https://wiki.openstreetmap.org/wiki/Overpass_API

# overpass_url = "https://overpass.kumi.systems/api/interpreter"
overpass_url = "http://overpass-api.de/api/interpreter"


# query_template : queries all objects in a distance (as radius) around the point (lat,lng)

query_teplate = """
[out:json];
 nwr(around:{distance},{lat},{lng});
out body;
"""


def ask_osm(query, url=overpass_url):
    """Queries the Overpass API with a query string

    :param query: an overpass query string
    :param url:   API address
    :return:      query results in json
    """
    result = requests.get(url, params={'data': query})
    if result.status_code != 200:
        return None
    else:
        return result.json()


def ask_osm_around_point(lat, lng, distance=100, url=overpass_url):
    """Queries the Overpass API around a point with a distance as radius

    :param lat:      wgs84 latitude
    :param lng:      wgs84 longitude
    :param distance: radius in meters
    :param url:      API address
    :return:         query results in json
    """
    return ask_osm(query_teplate.format(distance=distance, lat=lat, lng=lng), url=url)


def ask_osm_around_point_df(df_row, distance=100, url=overpass_url):
    """Queries the Overpass API around a point with a distance as radius, given in a dataframe

    Examaple:
    df.T.apply(ask_osm_around_point_df) or  df.apply(ask_osm_around_point_df, axis = 1)

    :param df_row:   a dataframe row with wgs84 coordinates in fields named lat, lng
    :param distance: radius in meters
    :param url:      API address
    :return:         query results in json
    """
    return ask_osm_around_point(lat=df_row.lat, lng=df_row.lng, distance=distance, url=url)


def ask_osm_around_point_np(coord_row, distance=100, lat_index=0, lng_index=1, url=overpass_url):
    """Queries the Overpass API around a point with a distance as radius, given in a np array of coords

    Example:
    np.apply_along_axis(ask_osm_around_point_np, 1, coords)

    :param coord_row: a numpy array row with wgs84 coordinates in fields at lat_index, lng_index
    :param distance:  radius in meters
    :param lat_index: index of latitude coordinate
    :param lng_index: index of longitude coordinate
    :param url:       API address
    :return:          query results in json
    """
    return ask_osm_around_point(lat=coord_row[lat_index], lng=coord_row[lng_index], distance=distance, url=url)
