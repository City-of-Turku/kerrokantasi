
import json

from django.contrib.gis.geos import GEOSGeometry, GeometryCollection


def get_geometry_from_geojson(geojson):
    gc = GeometryCollection()
    if geojson is None:
        return None
    print(f'geojson {geojson}')
    geometry_data = geojson.get('geometry', None) or geojson
    '''
    if geometry_data.get('features'):
        eka = geometry_data.get('features')
        toka = eka[0].get('geometry')
        geometry = GEOSGeometry(json.dumps(toka))
        gc.append(geometry)
        print(f'geometry {geometry}')
    '''
    if geometry_data.get('features'):
        for feat in geometry_data.get('features'):
                    geot = feat.get('geometry')
                    geo = GEOSGeometry(json.dumps(geot))
                    gc.append(geo)
    else:
        geometry = GEOSGeometry(json.dumps(geometry_data))
        gc.append(geometry)
    return gc
