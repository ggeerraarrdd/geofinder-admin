import psycopg2
from psycopg2.extras import RealDictCursor


def get_admin_geofinder_header(db):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT 
        SUM(CASE WHEN loc_playable = FALSE THEN 1 ELSE 0 END) AS loc_playable, 
        SUM(CASE WHEN loc_url_valid = FALSE THEN 1 ELSE 0 END) AS loc_url_valid, 
        SUM(CASE WHEN loc_image_valid = FALSE THEN 1 ELSE 0 END) AS loc_image_valid, 
        SUM(CASE WHEN loc_key_shp_valid = FALSE THEN 1 ELSE 0 END) AS loc_key_shp_valid 
        FROM locations; 
        """
    
    # Run query
    cursor.execute(query, (id,))

    # Get results
    results = cursor.fetchone()

    cursor.close()
    conn.close()

    return(results)


def get_admin_geofinder_content(db):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT 
            g.*,
            l.*
        FROM geofinder AS g 
        JOIN locations AS l ON g.geofinder_locations_id = l.id 
        ORDER BY g.geofinder_date
        ;
        """

    # Run query
    cursor.execute(query)

    # Get results
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


def get_admin_geofinder_loc(db, id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT * 
        FROM locations
        WHERE id = %s
        ; 
        """

    # Run query
    cursor.execute(query, (id,))

    # Get results
    results = cursor.fetchone()

    cursor.close()
    conn.close()

    return(results) #81

