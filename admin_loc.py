import json
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import geopandas as gpd
from shapely.geometry import Polygon
import shapely.wkb
from math import radians, degrees, cos, sqrt


def get_admin_loc_info(db, id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = "SELECT * FROM locations WHERE id = %s; "

    # Run query
    cursor.execute(query, (id,))

    # Get results
    results = cursor.fetchone()

    cursor.close()
    conn.close()

    return(results)


def get_admin_loc_polygon(shapefile):

    # Convert the PostGIS geometry into a Shapely geometry object
    geometry = shapely.wkb.loads(shapefile, hex=True)

    # Extract the polygon coordinates
    polygon_coordinates = list(geometry.exterior.coords)
    
    # Convert the polygon coordinates into a format suitable for the Google Maps API
    polygon = []
    for coordinate in polygon_coordinates:
        polygon.append({"lat": coordinate[1], "lng": coordinate[0]})
    
    # Convert the Google Maps polygon to JSON
    results = json.dumps(polygon)  

    return results


def get_admin_loc_corners(latitude, longitude):
    R = 6371.0  # Radius of the Earth in kilometers

    # Convert latitude and longitude to radians
    lat_rad = radians(latitude)
    lon_rad = radians(longitude)

    # Calculate the distance (in kilometers) to each corner of the box
    diagonal_distance = 0.01 * sqrt(2)
    half_diagonal_distance = diagonal_distance / 2
    north_distance = half_diagonal_distance / R
    east_distance = half_diagonal_distance / (R * cos(lat_rad))

    # Calculate the coordinates of the corners
    north_lat = latitude + degrees(north_distance)
    south_lat = latitude - degrees(north_distance)
    east_lon = longitude + degrees(east_distance)
    west_lon = longitude - degrees(east_distance)

    polygon = [
        {
            # northwest
            "lat": north_lat,
            "lng": west_lon
        },
        {
            # northeast
            "lat": north_lat,
            "lng": east_lon
        },
        {
            # southeast
            "lat": south_lat,
            "lng": east_lon
        },
        {
            # southwest
            "lat": south_lat,
            "lng": west_lon
        }
    ]

    return polygon


def get_admin_loc_shapefile_saved(db, coordinates, loc_id):

    # Create a GeoDataFrame with a single polygon from the property_coordinates list
    polygon = Polygon([(coord['lng'], coord['lat']) for coord in coordinates])
    gdf = gpd.GeoDataFrame(geometry=[polygon])

    # Save the GeoDataFrame as a shapefile
    # gdf.to_file('property_polygon.shp', driver='ESRI Shapefile')

    # Connect to the PostgreSQL database
    connection = psycopg2.connect(db)
    cursor = connection.cursor()

    query = """
        UPDATE locations SET 
        loc_key_shp = ST_GeomFromText('{}'), 
        loc_key_shp_valid = TRUE, 
        loc_date_updated = CURRENT_TIMESTAMP 
        WHERE id = %s RETURNING id, loc_key_shp; 
        """

    for i, row in gdf.iterrows():
        cursor.execute(sql.SQL(query).format(sql.SQL(row['geometry'].wkt)), (loc_id,))

    results = cursor.fetchone()

    if id:
        query = """
            UPDATE locations SET 
            loc_key_lat = ROUND((SELECT ST_Y(ST_Centroid(loc_key_shp))::NUMERIC FROM locations WHERE id = %s), 6),
            loc_key_lng = ROUND((SELECT ST_X(ST_Centroid(loc_key_shp))::NUMERIC FROM locations WHERE id = %s), 6),
            loc_key_coor = (SELECT ST_AsText(ST_Centroid(loc_key_shp)) FROM locations WHERE id = %s),
            loc_key_shp_valid = TRUE
            WHERE id = %s 
            RETURNING loc_key_shp;
            """
        
        cursor.execute(query, (results[0], results[0], results[0], results[0]))

    # Commit the changes
    connection.commit()

    # Close the connection
    cursor.close()
    connection.close()

    return results[1]


def get_admin_loc_add_geofinder(db, id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query 1
    query = """
        INSERT INTO geofinder (geofinder_date, geofinder_locations_id) VALUES 
        ((SELECT MAX(geofinder_date) + 1 FROM geofinder), %s)
        ;
        """

    # Run query 1
    cursor.execute(query, (id,))

    # Set query 2
    query = """
        UPDATE locations
        SET loc_game = 'geofinder' 
        WHERE id = %s
        ;
        """

    # Run query 2
    cursor.execute(query, (id,))

    # Commit the changes
    conn.commit()

    cursor.close()
    conn.close()

    return 1

