import psycopg2
from psycopg2.extras import RealDictCursor


def get_admin_main_header(db):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query 
    query = """
        SELECT 
            (SELECT CURRENT_TIMESTAMP::date) AS admin_main_header_today,
            (SELECT SUM(CASE WHEN loc_playable = FALSE THEN 1 ELSE 0 END) FROM locations WHERE loc_game = 'geofinder') AS admin_main_header_geofinder,
            (SELECT SUM(CASE WHEN loc_playable = FALSE THEN 1 ELSE 0 END) FROM locations WHERE loc_game = 'geo50x') AS admin_main_header_fifty,
            (SELECT SUM(CASE WHEN loc_playable = FALSE THEN 1 ELSE 0 END) FROM locations) AS admin_main_header_locations
        ;
        """
    
    # Run query
    cursor.execute(query, (id,))

    # Get results
    results = cursor.fetchone()

    cursor.close()
    conn.close()

    return results


def get_admin_main_content(db):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT 
            g.*,
            l.id,
            l.loc_playable,
            l.loc_city,
            l.loc_state,
            l.loc_country
        FROM geofinder AS g 
        JOIN locations AS l ON g.geofinder_locations_id = l.id 
        WHERE geofinder_date >= CURRENT_TIMESTAMP::date
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

