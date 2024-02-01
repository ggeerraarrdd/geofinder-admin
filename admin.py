import psycopg2
from psycopg2.extras import RealDictCursor
from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        
        if session.get("status") != 'admin':
            return redirect("/login")
        
        return f(*args, **kwargs)
    return decorated_function


def get_registered(db, new_username, new_password):

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


def get_admin_login_user_info(db, user_id):

    conn = psycopg2.connect(db)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Set query
    query = """
        SELECT * 
        FROM users 
        WHERE username = %s 
        AND status = 'admin'; 
        """

    # Run query
    cursor.execute(query, (user_id,))

    # Get results
    user_info = cursor.fetchone()

    cursor.close()
    conn.close()

    return(user_info)

