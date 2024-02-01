import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd


def get_admin_users_header(db):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        WITH games_fifty AS 
            ( 
            SELECT u.id, u.username, u.date_add, MAX(g.fifty_game_end) AS last_game_date 
            FROM games_fifty AS g 
            RIGHT JOIN users AS u ON g.fifty_game_user_id = u.id 
            GROUP BY u.id 
            ),
        games_geofinder AS 
            (
            SELECT u.id, u.username, u.date_add, MAX(gg.geo_game_end) AS last_game_date 
            FROM games_geofinder AS gg 
            RIGHT JOIN users AS u ON gg.geo_game_user_id = u.id 
            GROUP BY u.id
            )
        SELECT  
            COUNT(*) AS user_count, 
            SUM(CASE WHEN EXTRACT(DAY FROM AGE(CURRENT_DATE, COALESCE(fg.last_game_date, gg.last_game_date))) < 8 THEN 1 ELSE 0 END) AS users_active,
            EXTRACT(DAY FROM AGE(CURRENT_DATE, MAX(fg.date_add))) AS last_user_registration, 
            EXTRACT(DAY FROM AGE(CURRENT_DATE, MAX(fg.last_game_date))) AS fifty_last_user_game,
            EXTRACT(DAY FROM AGE(CURRENT_DATE, MAX(gg.last_game_date))) AS geofinder_last_user_game 
        FROM games_fifty AS fg
        JOIN games_geofinder AS gg ON fg.id = gg.id;  
        """
    
    # Run query
    cursor.execute(query)

    # Get results
    results = cursor.fetchone()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return results


def get_admin_users_content(db):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT 
            u.id, 
            u.status, 
            u.username, 
            u.country, 
            u.icon, 
            TO_CHAR(u.date_add, 'YYYY-MM-DD') date_add, 
            EXTRACT(DAY FROM AGE(CURRENT_DATE, MAX(g.game_end))) AS last_game_date 
        FROM games AS g 
        RIGHT JOIN users AS u ON g.user_id = u.id 
        GROUP BY u.id 
        ORDER BY u.id; 
        """

    # Run query
    cursor.execute(query)

    # Get results
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


def get_admin_user_header_profile(db, user_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT id, username, status, date_add, country, icon
        FROM users 
        WHERE id = %s;
        """
    
    # Run query
    cursor.execute(query, (user_id,))

    # Get results
    results = cursor.fetchone()

    cursor.close()
    conn.close()

    return results


def get_admin_user_add(db, new_username, new_password):

    # Create connection and cursor
    conn = psycopg2.connect(db)
    cursor = conn.cursor()

    # Create query
    query = "INSERT INTO users (username, hash) "
    query = query + "VALUES (%s, %s); "

    # Execute query
    cursor.execute(query, (new_username, new_password))

    # Commit insert
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    return 1


def get_admin_user_header_geofinder(db, user_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        WITH profile AS 
            (
            WITH cte AS 
                ( 
                SELECT 
                    geo_game_user_id,
                    geo_game_geofinder_id,
                    MIN(geo_game_start) AS geo_game_datetime_min,
                    MAX(geo_game_end) AS geo_game_datetime_max
                FROM games_geofinder 
                WHERE geo_game_user_id = %s
                GROUP BY geo_game_user_id, geo_game_geofinder_id
                ORDER BY geo_game_user_id, geo_game_geofinder_id
                ) 
            SELECT 
                g.*,
                TO_CHAR(c.geo_game_datetime_max - c.geo_game_datetime_min, 'HH24:MI:SS') AS geo_game_duration_total,
                gg.geo_game_submit_validation 
            FROM geofinder AS g 
            LEFT JOIN cte AS c ON g.geofinder_id = c.geo_game_geofinder_id 
            LEFT JOIN games_geofinder AS gg ON c.geo_game_datetime_max =  gg.geo_game_end
            WHERE g.geofinder_date <= (CURRENT_TIMESTAMP AT TIME ZONE 'US/Central')::date 
            AND g.geofinder_date >= (SELECT date_add::date as date FROM users WHERE id = %s)
            ORDER BY g.geofinder_date DESC
            )
        SELECT 
            * 
        FROM profile AS p; 
        """

    # Run query
    cursor.execute(query, (user_id, user_id,))

    # Get data
    data = cursor.fetchall()

    # Initialize results
    results = {
        "total_found": 0,
        "current_streak": 0,
        "longest_streak": 0,
        "fastest_time": 0
    }

    if (len(data) > 0):
        # Get results
        df = pd.DataFrame(data)

        # Total Count
        try:
            total_count =  df['geo_game_submit_validation'].value_counts()[1]
        except:
            total_count = 0

        # Current Streak
        try:
            df_current = df.copy()

            # Remove first row if geo_game_submit_validation is null
            if pd.isnull(df_current.loc[0, 'geo_game_submit_validation']):
                df_current = df_current.drop(df_current.index[0]).reset_index(drop=True)

            # Remove first row if not yet found or quit
            if df_current['geo_game_submit_validation'].iloc[0] == 0:
                df_current.iloc[1:]
            else:
                df_current

            # Get current streak
            if df_current['geo_game_submit_validation'].nunique() == 1:
                current_streak = df_current['geo_game_submit_validation'].sum()
            else:
                current_streak = (df_current['geo_game_submit_validation'] != 1).argmax()

        except:
            current_streak = 0

        # Longest Streak
        try:
            df_longest = df.copy()

            df_longest['geo_game_submit_validation'] = df_longest['geo_game_submit_validation'].fillna(0)
            df_longest['group'] = (df_longest['geo_game_submit_validation'] != df_longest['geo_game_submit_validation'].shift()).cumsum()

            longest_streak = df_longest[df_longest['geo_game_submit_validation'] == 1]['group'].value_counts().max()
            
            try:
                longest_streak = int(longest_streak)
            except:
                longest_streak = 0

        except:
            longest_streak = 0


        # Fastest Time 
        try:

            df_fastest = df.copy()

            df_fastest = df_fastest[df_fastest['geo_game_submit_validation'] == 1]

            df_fastest = df_fastest.dropna(subset=['geo_game_duration_total'])
                  
            df_fastest['geo_game_duration_total'] = pd.to_datetime(df_fastest['geo_game_duration_total'], format='%H:%M:%S', errors='coerce').dt.time

            fastest_time = df_fastest['geo_game_duration_total'].min()

        except:
            fastest_time = 0

        # Update results
        results["total_found"] = total_count
        results["current_streak"] = int(current_streak)
        results["longest_streak"] = longest_streak
        results["fastest_time"] = fastest_time
    
    # Close cursor and connection
    cursor.close()
    conn.close()

    return(results)


def get_admin_user_header_fifty(db, user_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT 
            SUM(CASE WHEN game_answer_validation > 0 THEN 1 ELSE 0 END) AS user_count_loc, 
            SUM(CASE WHEN game_answer_validation > 0 THEN game_score ELSE 0 END) AS user_score_total, 
            SUM(CASE WHEN game_answer_validation > 0 THEN 1 ELSE 0 END) * 100 AS user_score_possible, 
            CASE WHEN SUM(CASE WHEN game_answer_validation > 0 THEN 1 ELSE 0 END) > 0 
                THEN ROUND(SUM(CASE WHEN game_answer_validation > 0 THEN game_score ELSE 0 END) / SUM(CASE WHEN game_answer_validation > 0 THEN 1 ELSE 0 END), 1) 
                ELSE 0 
                END AS user_score_percentage, 
            COALESCE(SUM(game_duration), 0) AS user_duration_total, 
            COALESCE(AVG(game_duration), 0) AS user_duration_average, 
            COALESCE(ROUND(SUM(game_answer_off)::NUMERIC / count(*)), 0) AS user_offset_avg, 
            TO_CHAR(MAX(game_end), 'YYYY-MM-DD') AS last_game, 
            EXTRACT(DAY FROM AGE(CURRENT_DATE, MAX(game_end))) AS days 
        FROM games 
        WHERE user_id = %s; 
        """

    # Run query
    cursor.execute(query, (user_id,))

    # Get results
    results = cursor.fetchone()

    cursor.close()
    conn.close()

    return results


def get_admin_user_updated_username(db, username, id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        UPDATE users SET 
        username = %s, 
        date_updated = CURRENT_TIMESTAMP 
        WHERE id = %s;
        """
    
    # Run query
    cursor.execute(query, (username, id))

    # Commit update
    conn.commit()

    cursor.close()
    conn.close()

    return 1


def get_admin_user_updated_country(db, country, id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        UPDATE users SET 
        country = %s, 
        date_updated = CURRENT_TIMESTAMP 
        WHERE id = %s; 
        """

    # Run query
    cursor.execute(query, (country, id))

    # Commit update
    conn.commit()

    cursor.close()
    conn.close()

    return 1


def get_admin_user_updated_password(db, password, id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        UPDATE users SET 
        hash = %s, 
        date_updated = CURRENT_TIMESTAMP 
        WHERE id = %s; 
        """

    # Run query
    cursor.execute(query, (password, id))

    # Commit update
    conn.commit()

    cursor.close()
    conn.close()

    return 1

