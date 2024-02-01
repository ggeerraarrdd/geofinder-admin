import psycopg2
from psycopg2.extras import RealDictCursor
import requests


def get_admin_locations_validated(db):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Insert values from get_playable_location to games table
    query = "SELECT * FROM locations ORDER BY id; "
    cursor.execute(query)
    rows = cursor.fetchall()

    # # Validate loc_url_source
    # print("VALIDATE URLS")
    # for row in rows:
    #     id, url = row["id"], row["loc_url_source"]
    #     try:
    #         response = requests.get(url)
    #         print(response)
    #         if response.status_code == 200:
    #             update_query = f"UPDATE locations SET loc_url_valid = TRUE WHERE id = {id}; "
    #             cursor.execute(update_query)
    #             print(f"{id} is accessible.")
    #         else:
    #             # Update loc_url_valid if URL is not accessible
    #             update_query = f"UPDATE locations SET loc_url_valid = FALSE WHERE id = {id}; "
    #             cursor.execute(update_query)
    #             print(f"{id} is not accessible. The loc_url_valid column has been updated.")
    #     except requests.exceptions.RequestException:
    #         print("except")
    #         # Update the column in that row to indicate the URL is not accessible
    #         update_query = f"UPDATE locations SET loc_url_valid = FALSE WHERE id = {id}; "
    #         cursor.execute(update_query)
    #         print(f"{id} is not accessible. The is_active column has been updated.")
    
    # # Validate is_playable
    # print("VALIDATE IMAGES")
    # for row in rows:
    #     id, url = row["id"], row["loc_image_source"]
    #     try:
    #         response = requests.get(url)
    #         if response.status_code == 200:
    #             update_query = f"UPDATE locations SET loc_image_valid = TRUE WHERE id = {id}; "
    #             cursor.execute(update_query)
    #             print(f"{id} is accessible.")
    #         else:
    #             # Update is_active if URL is not accessible
    #             update_query = f"UPDATE locations SET loc_image_valid = FALSE WHERE id = {id}; "
    #             cursor.execute(update_query)
    #             print(f"{id} is not accessible. The loc_image_valid column has been updated.")
    #     except requests.exceptions.RequestException:
    #         # Update the column in that row to indicate the URL is not accessible
    #         update_query = f"UPDATE locations SET loc_image_valid = FALSE WHERE id = {id}; "
    #         cursor.execute(update_query)
    #         print(f"{id} is not accessible. The accessibility column has been updated.")

    # Validate locations
    print("VALIDATE LOCATIONS")
    for row in rows:
        id = row["id"]
        playable = row["loc_playable"]
        removed = row["loc_removed"]
        url = row["loc_url_valid"]
        image = row["loc_image_valid"]
        key = row["loc_key_shp_valid"]

        if (not removed) and (url) and (image) and (key):
            if not playable:
                update_query = f"UPDATE locations SET loc_playable = TRUE WHERE id = {id}; "
                cursor.execute(update_query)
                print(f"{id} is playable. The loc_playable column has been updated")
            else:
                print(f"{id} is playable.")
        else:
            if playable:
                update_query = f"UPDATE locations SET loc_playable = FALSE WHERE id = {id}; "
                cursor.execute(update_query)
                print(f"{id} is not playable. The loc_playable column has been updated")
            else:
                print(f"{id} is not playable.")

    # Commit the changes
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return 1


def get_admin_locations_content_all(db):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT * FROM locations ORDER BY id DESC;
        """

    # Run query
    cursor.execute(query)

    # Get results
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


def get_admin_locations_content_avail(db):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT * 
        FROM locations 
        WHERE loc_game IS NULL 
        ORDER BY id;
        """

    # Run query
    cursor.execute(query)

    # Get results
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


def get_admin_locations_content_avail_play(db):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT * 
        FROM locations 
        WHERE loc_game IS NULL
        AND loc_playable
        ORDER BY id;
        """

    # Run query
    cursor.execute(query)

    # Get results
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


def get_admin_locations_content_avail_notplay(db):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT * 
        FROM locations 
        WHERE loc_game IS NULL
        AND NOT loc_playable
        ORDER BY id;
        """

    # Run query
    cursor.execute(query)

    # Get results
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

