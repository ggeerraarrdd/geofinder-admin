import os
import json
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from pprint import pp

# from helpers import apology, login_required
from scraper import get_admin_loc_add

from admin import apology, login_required, get_admin_login_user_info
import admin_main
import admin_geo
import admin_fifty
import admin_locations
import admin_loc
import admin_users


# Configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

# View HTML changes without rerunning server
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Get environmental variables
map_api_key = os.environ.get("MAP_API_KEY")
host = os.environ.get("GEOFINDER_DB_HOST")
port = os.environ.get("GEOFINDER_DB_PORT")
database = os.environ.get("GEOFINDER_DB_NAME")
user = os.environ.get("GEOFINDER_DB_USER")
password = os.environ.get("GEOFINDER_DB_PASSWORD")

# Set database
db_pg = f'postgresql://{user}:{password}@{host}:{port}/{database}'

# Set registration status
try:
    new_registrations = False if os.environ.get("NEW_REGISTRATIONS").upper() == "FALSE" else True
except:
    new_registrations = False


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


####################################################################
# 
# /
#
####################################################################
@app.route("/", methods=["GET", "POST"])
@login_required
def start():

    if request.method == "POST":

        bttn = request.form.get("bttn")

        if (bttn == "admin_main"):
            
            try:
                session["get_admin_main_header"]
                session["get_admin_main_content"]
            except KeyError:
                get_admin_main_header = admin_main.get_admin_main_header(db_pg)
                get_admin_main_content = admin_main.get_admin_main_content(db_pg)

                session["get_admin_main_header"] = get_admin_main_header
                session["get_admin_main_content"] = get_admin_main_content
            
            return redirect("/admin/main")

        elif (bttn == "admin_geofinder"):

            try:
                session["get_admin_geofinder_header"]
                session["get_admin_geofinder_content"]
            except KeyError:
                get_admin_geofinder_header = admin_geo.get_admin_geofinder_header(db_pg)
                get_admin_geofinder_content = admin_geo.get_admin_geofinder_content(db_pg)

                # Save package to session
                session["get_admin_geofinder_header"] = get_admin_geofinder_header
                session["get_admin_geofinder_content"] = get_admin_geofinder_content

            return redirect("/admin/geofinder")
        
        elif (bttn == "admin_fifty"):

            try:
                session["get_admin_fifty_header"] 
                session["get_admin_fifty_content"]
            except KeyError:
                get_admin_fifty_header = admin_fifty.get_admin_fifty_header(db_pg)
                get_admin_fifty_content = admin_fifty.get_admin_fifty_content_(db_pg)

                # Save packages to session
                session["get_admin_fifty_header"] = get_admin_fifty_header
                session["get_admin_fifty_content"] = get_admin_fifty_content

            return redirect("/admin/fifty")
        
        elif (bttn == "admin_locations"):

            try:
                session["get_admin_locations_content"] = session["get_admin_locations_content_all"]
                session["get_admin_locations_content_avail"]
                session["get_admin_locations_content_avail_play"]
                session["get_admin_locations_content_avail_notplay"]
            except KeyError:
                get_admin_locations_content_all = admin_locations.get_admin_locations_content_all(db_pg)
                get_admin_locations_content_avail = admin_locations.get_admin_locations_content_avail(db_pg)
                get_admin_locations_content_avail_play = admin_locations.get_admin_locations_content_avail_play(db_pg)
                get_admin_locations_content_avail_notplay = admin_locations.get_admin_locations_content_avail_notplay(db_pg)

                # Save packages to session
                session["get_admin_locations_content"] = get_admin_locations_content_all
                session["get_admin_locations_content_all"] = get_admin_locations_content_all
                session["get_admin_locations_content_avail"] = get_admin_locations_content_avail
                session["get_admin_locations_content_avail_play"] = get_admin_locations_content_avail_play
                session["get_admin_locations_content_avail_notplay"] = get_admin_locations_content_avail_notplay

            session["get_admin_locations_content_active"] = "content_all"

            return redirect("/admin/locations")
        
        elif (bttn == "admin_users"):

            try:
                session["get_admin_users_header"]
                session["get_admin_users_content"]
            except KeyError:
                get_admin_users_header = admin_users.get_admin_users_header(db_pg)
                get_admin_users_content = admin_users.get_admin_users_content(db_pg)

                # Save package to session
                session["get_admin_users_header"] = get_admin_users_header
                session["get_admin_users_content"] = get_admin_users_content

            return redirect("/admin/users")
        
        elif (bttn == "refresh"):

            admin_locations.get_admin_locations_validated(db_pg)

            session["get_admin_main_content"] = admin_main.get_admin_main_content(db_pg)
            session["get_admin_geofinder_header"] = admin_geo.get_admin_geofinder_header(db_pg)
            session["get_admin_geofinder_content"] = admin_geo.get_admin_geofinder_content(db_pg)
            session["get_admin_fifty_header"] = admin_fifty.get_admin_fifty_header(db_pg)
            session["get_admin_fifty_content"] = admin_fifty.get_admin_fifty_content_(db_pg)
            session["get_admin_locations_content"] = admin_locations.get_admin_locations_content_all(db_pg)
            session["get_admin_locations_content_all"] = admin_locations.get_admin_locations_content_all(db_pg)
            session["get_admin_locations_content_avail"] = admin_locations.get_admin_locations_content_avail(db_pg)
            session["get_admin_locations_content_avail_play"] = admin_locations.get_admin_locations_content_avail_play(db_pg)
            session["get_admin_locations_content_avail_notplay"] = admin_locations.get_admin_locations_content_avail_notplay(db_pg)

            return redirect("/")

        else:

            return redirect("/")

    else:

        # Set package
        get_admin_main_header = admin_main.get_admin_main_header(db_pg)
        get_admin_main_content = admin_main.get_admin_main_content(db_pg)

        # Save package to Session
        session["get_admin_main_header"] = get_admin_main_header
        session["get_admin_main_content"] = get_admin_main_content

        return redirect("/admin/main")


####################################################################
# 
# ADMIN - MAIN
#
####################################################################
@app.route("/admin/main", methods=["GET", "POST"])
@login_required
def admin__main():

    if request.method == "POST":

        return redirect("/")
       
    else:

        # Get packages from Session
        get_admin_main_header = session["get_admin_main_header"]
        get_admin_main_content = session["get_admin_main_content"]

        return render_template("admin_main.html", 
                                map_api_key=map_api_key,
                                get_admin_main_header=get_admin_main_header,
                                get_admin_main_content=get_admin_main_content)
        

####################################################################
# 
# ADMIN - GEOFINDER
#
####################################################################
@app.route("/admin/geofinder", methods=["GET", "POST"])
@login_required
def admin__geo():
    """Show user history of games """

    if request.method == "POST":
            
        bttn = request.form.get("bttn")

        if (bttn == "admin_loc"):
 
            loc_id = int(request.form.get("loc-edit"))

            if loc_id > 0:

                loc_info= admin_loc.get_admin_loc_info(db_pg, loc_id)

                if loc_info["loc_key_shp"]: 

                    get_admin_loc_polygon = admin_loc.get_admin_loc_polygon(loc_info["loc_key_shp"])

                else:

                    if loc_info["loc_key_lat"]:
                        lat = loc_info["loc_key_lat"]
                        lng = loc_info["loc_key_lng"]
                    else:
                        lat = loc_info["loc_view_lat"]
                        lng = loc_info["loc_view_lng"]

                    get_admin_loc_polygon = admin_loc.get_admin_loc_corners(float(lat), 
                                                                          float(lng))
                    
                    get_admin_loc_polygon = json.dumps(get_admin_loc_polygon)   
            
                session["get_admin_loc_info"] = loc_info
                session["get_admin_loc_polygon"] = get_admin_loc_polygon

                return redirect("/admin/loc")

            else:

                return redirect("/")
        
        else:

            return redirect("/")
    
    else:

        # Get packages from Session
        get_admin_geofinder_header = session["get_admin_geofinder_header"]
        get_admin_geofinder_content = session["get_admin_geofinder_content"]

        return render_template("admin_geofinder.html", 
                                page="admin_fifty", 
                                map_api_key=map_api_key,
                                get_admin_geofinder_header=get_admin_geofinder_header,
                                get_admin_geofinder_content=get_admin_geofinder_content)
 

####################################################################
# 
# ADMIN - GEO50x
#
####################################################################
@app.route("/admin/fifty", methods=["GET", "POST"])
@login_required
def admin__fifty():
    """Show user history of games """

    if request.method == "POST":

        loc_id = int(request.form.get("loc-edit"))

        if loc_id > 0:

            loc_info= admin_loc.get_admin_loc_info(db_pg, loc_id)

            if loc_info["loc_key_shp"]: 

                get_admin_loc_polygon = admin_loc.get_admin_loc_polygon(loc_info["loc_key_shp"])

            else:

                if loc_info["loc_key_lat"]:
                    lat = loc_info["loc_key_lat"]
                    lng = loc_info["loc_key_lng"]
                else:
                    lat = loc_info["loc_view_lat"]
                    lng = loc_info["loc_view_lng"]

                get_admin_loc_polygon = admin_loc.get_admin_loc_corners(float(lat), 
                                                                        float(lng))
                
                get_admin_loc_polygon = json.dumps(get_admin_loc_polygon)   
        
            # Save page config to Session
            session["requester"] = "admin_fifty"

            # Save packages to Session
            session["get_admin_loc_info"] = loc_info
            session["get_admin_loc_polygon"] = get_admin_loc_polygon

            return redirect("/admin/loc")

        else:

            return redirect("/")
    
    else:

        # Get packages from Session
        get_admin_fifty_header = session["get_admin_fifty_header"]
        get_admin_fifty_content = session["get_admin_fifty_content"]

        return render_template("admin_fifty.html", 
                                page="admin_fifty", 
                                map_api_key=map_api_key,
                                get_admin_fifty_header=get_admin_fifty_header,
                                get_admin_fifty_content=get_admin_fifty_content)


####################################################################
# 
# ADMIN - LOCATIONS
#
####################################################################
@app.route("/admin/locations", methods=["GET", "POST"])
@login_required
def admin__locations():

    if request.method == "POST":
        
        active = request.form.get("active")
        bttn = request.form.get("bttn")

        if (bttn == "admin_loc"):
 
            loc_id = int(request.form.get("loc-edit"))

            if loc_id > 0:

                loc_info= admin_loc.get_admin_loc_info(db_pg, loc_id)

                if loc_info["loc_key_shp"]: 

                    get_admin_loc_polygon = admin_loc.get_admin_loc_polygon(loc_info["loc_key_shp"])

                else:

                    if loc_info["loc_key_lat"]:
                        lat = loc_info["loc_key_lat"]
                        lng = loc_info["loc_key_lng"]
                    else:
                        lat = loc_info["loc_view_lat"]
                        lng = loc_info["loc_view_lng"]

                    get_admin_loc_polygon = admin_loc.get_admin_loc_corners(float(lat), 
                                                                          float(lng))
                    
                    get_admin_loc_polygon = json.dumps(get_admin_loc_polygon)   
            
                # Save page config to Session
                session["requester"] = active

                # Save packages to Session
                session["get_admin_loc_info"] = loc_info
                session["get_admin_loc_polygon"] = get_admin_loc_polygon

                return redirect("/admin/loc")

            else:

                return redirect("/")
        
        elif (bttn == "admin_locations_add"):

            url = request.form.get("url")

            try:            
                loc_id = get_admin_loc_add(db_pg, url)
            except:
                print("error adding new loc")
                return redirect("/admin/locations")

            get_admin_locations_content_all = admin_locations.get_admin_locations_content_all(db_pg)
            get_admin_locations_content_avail = admin_locations.get_admin_locations_content_avail(db_pg)
            get_admin_locations_content_avail_play = admin_locations.get_admin_locations_content_avail_play(db_pg)
            get_admin_locations_content_avail_notplay = admin_locations.get_admin_locations_content_avail_notplay(db_pg)

            # Save updated packages to Session
            session["get_admin_locations_content_all"] = get_admin_locations_content_all
            session["get_admin_locations_content_avail"] = get_admin_locations_content_avail
            session["get_admin_locations_content_avail_play"] = get_admin_locations_content_avail_play
            session["get_admin_locations_content_avail_notplay"] = get_admin_locations_content_avail_notplay
        
            if loc_id > 0:

                loc_info= admin_loc.get_admin_loc_info(db_pg, loc_id)

                if loc_info["loc_key_shp"]: 

                    get_admin_loc_polygon = admin_loc.get_admin_loc_polygon(loc_info["loc_key_shp"])

                else:

                    if loc_info["loc_key_lat"]:
                        lat = loc_info["loc_key_lat"]
                        lng = loc_info["loc_key_lng"]
                    else:
                        lat = loc_info["loc_view_lat"]
                        lng = loc_info["loc_view_lng"]

                    get_admin_loc_polygon = admin_loc.get_admin_loc_corners(float(lat), 
                                                                          float(lng))
                    
                    get_admin_loc_polygon = json.dumps(get_admin_loc_polygon)   
            
                # Save page config to Session
                session["requester"] = active

                # Save packages to Session
                session["get_admin_loc_info"] = loc_info
                session["get_admin_loc_polygon"] = get_admin_loc_polygon

                return redirect("/admin/loc")

            else:

                return redirect("/")
        
        elif (bttn == "admin_locations_validated"):

            admin_locations.get_admin_locations_validated(db_pg)

            get_admin_locations_content_all = admin_locations.get_admin_locations_content_all(db_pg)
            get_admin_locations_content_avail = admin_locations.get_admin_locations_content_avail(db_pg)
            get_admin_locations_content_avail_play = admin_locations.get_admin_locations_content_avail_play(db_pg)
            get_admin_locations_content_avail_notplay = admin_locations.get_admin_locations_content_avail_notplay(db_pg)

            # Save updated packages to Session
            session["get_admin_locations_content_all"] = get_admin_locations_content_all
            session["get_admin_locations_content_avail"] = get_admin_locations_content_avail
            session["get_admin_locations_content_avail_play"] = get_admin_locations_content_avail_play
            session["get_admin_locations_content_avail_notplay"] = get_admin_locations_content_avail_notplay

            if (active == "content_all"):
                session["get_admin_locations_content"] = get_admin_locations_content_all
            elif (active == "content_avail"):
                session["get_admin_locations_content"] = get_admin_locations_content_avail
            elif (active == "content_avail_play"):
                session["get_admin_locations_content"] = get_admin_locations_content_avail_play
            elif (active == "content_avail_notplay"):
                session["get_admin_locations_content"] = get_admin_locations_content_avail_notplay
            else:
                session["get_admin_locations_content"] = get_admin_locations_content_all

            return redirect("/admin/locations")

        elif (bttn == "admin_locations_all"):

            try:
                session["get_admin_locations_content_all"]
            except KeyError:
                session["get_admin_locations_content_all"] = admin_locations.get_admin_locations_content_all(db_pg)

            session["get_admin_locations_content_active"] = "content_all"
            session["get_admin_locations_content"] = session["get_admin_locations_content_all"]

            return redirect("/admin/locations")

        elif (bttn == "admin_locations_avail"):

            try:
                session["get_admin_locations_content_avail"]
            except KeyError:
                session["get_admin_locations_content_avail"] = admin_locations.get_admin_locations_content_avail(db_pg)

            session["get_admin_locations_content_active"] = "content_avail"
            session["get_admin_locations_content"] = session["get_admin_locations_content_avail"]

            return redirect("/admin/locations")
        
        elif (bttn == "admin_locations_avail_play"):

            try:
                session["get_admin_locations_content_avail_play"]
            except KeyError:
                session["get_admin_locations_content_avail_play"] = admin_locations.get_admin_locations_content_avail_play(db_pg)

            session["get_admin_locations_content_active"] = "content_avail_play"
            session["get_admin_locations_content"] = session["get_admin_locations_content_avail_play"]

            return redirect("/admin/locations")

        elif (bttn == "admin_locations_avail_notplay"):

            try:
                session["get_admin_locations_content_avail_notplay"]
            except KeyError:
                session["get_admin_locations_content_avail_notplay"] = admin_locations.get_admin_locations_content_avail_notplay(db_pg)

            session["get_admin_locations_content_active"] = "content_avail_notplay"
            session["get_admin_locations_content"] = session["get_admin_locations_content_avail_notplay"]

            return redirect("/admin/locations")
        
        else:

            return redirect("/")
    
    else:

        active = session["get_admin_locations_content_active"]
        get_admin_locations_content = session["get_admin_locations_content"]
        get_admin_locations_content_all = session["get_admin_locations_content_all"]
        get_admin_locations_content_avail = session["get_admin_locations_content_avail"]
        get_admin_locations_content_avail_play = session["get_admin_locations_content_avail_play"]
        get_admin_locations_content_avail_notplay = session["get_admin_locations_content_avail_notplay"]

        return render_template("admin_locations.html", 
                                page="admin_locations", 
                                active=active,
                                map_api_key=map_api_key,
                                get_admin_locations_content=get_admin_locations_content,
                                get_admin_locations_content_all=get_admin_locations_content_all,
                                get_admin_locations_content_avail=get_admin_locations_content_avail,
                                get_admin_locations_content_avail_play=get_admin_locations_content_avail_play,
                                get_admin_locations_content_avail_notplay=get_admin_locations_content_avail_notplay)
 

####################################################################
# 
# ADMIN - LOC
#
####################################################################
@app.route("/admin/loc", methods=["GET", "POST"])
@login_required
def admin__loc():

    if request.method == "POST":

        active = bttn = request.form.get("active")
        bttn = request.form.get("bttn")

        if (bttn == "admin_loc_save"):

            loc_id = request.form.get("loc-id")
            property_coordinates = request.form.get("propertyCoordinates")

            if loc_id: 

                if property_coordinates:

                    # Convert string to list
                    property_coordinates = eval("[" + property_coordinates + "]")

                    # Convert to list of dicts
                    property_coordinates = [{"lat": lat, "lng": lng} for lat, lng in property_coordinates]

                    # Save shapefile
                    loc_key_shp = admin_loc.get_admin_loc_shapefile_saved(db_pg, property_coordinates, int(loc_id))

                    # Update package due to changes
                    get_admin_loc_info = admin_loc.get_admin_loc_info(db_pg, loc_id)
                    get_admin_loc_polygon = admin_loc.get_admin_loc_polygon(loc_key_shp)
                    get_admin_locations_content_all = admin_locations.get_admin_locations_content_all(db_pg)
                    get_admin_locations_content_avail = admin_locations.get_admin_locations_content_avail(db_pg)
                    get_admin_locations_content_avail_play = admin_locations.get_admin_locations_content_avail_play(db_pg)
                    get_admin_locations_content_avail_notplay = admin_locations.get_admin_locations_content_avail_notplay(db_pg)

                    # Save updated package to Session
                    session["get_admin_loc_info"] = get_admin_loc_info
                    session["get_admin_loc_polygon"] = get_admin_loc_polygon

                    # Save updated packages to Session
                    session["get_admin_locations_content_all"] = get_admin_locations_content_all
                    session["get_admin_locations_content_avail"] = get_admin_locations_content_avail
                    session["get_admin_locations_content_avail_play"] = get_admin_locations_content_avail_play
                    session["get_admin_locations_content_avail_notplay"] = get_admin_locations_content_avail_notplay

                    if (active == "content_all"):
                        session["get_admin_locations_content"] = get_admin_locations_content_all
                    elif (active == "content_avail"):
                        session["get_admin_locations_content"] = get_admin_locations_content_avail
                    elif (active == "content_avail_play"):
                        session["get_admin_locations_content"] = get_admin_locations_content_avail_play
                    elif (active == "content_avail_notplay"):
                        session["get_admin_locations_content"] = get_admin_locations_content_avail_notplay
                    else:
                        session["get_admin_locations_content"] = get_admin_locations_content_all

                    return redirect("/admin/loc")

                else:

                    return redirect("/admin/locations")
            
            else: 

                return redirect("/admin/locations")
        
        elif (bttn == "admin_loc_undo"):

            return redirect("/admin/loc")
        
        elif (bttn == "admin_loc_add_geofinder"):

            loc_id = request.form.get("loc-id")

            admin_loc.get_admin_loc_add_geofinder(db_pg, loc_id)

            admin_locations.get_admin_locations_validated(db_pg)

            # Update all packages and save to Session
            session["get_admin_main_content"] = admin_main.get_admin_main_content(db_pg)
            session["get_admin_geofinder_header"] = admin_geo.get_admin_geofinder_header(db_pg)
            session["get_admin_geofinder_content"] = admin_geo.get_admin_geofinder_content(db_pg)
            # session["get_admin_fifty_header"] = admin_fifty.get_admin_fifty_header(db_pg)
            # session["get_admin_fifty_content"] = admin_fifty.get_admin_fifty_content_(db_pg)
            session["get_admin_locations_content"] = admin_locations.get_admin_locations_content_all(db_pg)
            session["get_admin_locations_content_all"] = admin_locations.get_admin_locations_content_all(db_pg)
            session["get_admin_locations_content_avail"] = admin_locations.get_admin_locations_content_avail(db_pg)
            session["get_admin_locations_content_avail_play"] = admin_locations.get_admin_locations_content_avail_play(db_pg)
            session["get_admin_locations_content_avail_notplay"] = admin_locations.get_admin_locations_content_avail_notplay(db_pg)

            return redirect("/admin/geofinder")
        
        elif (bttn == "admin_loc_add_fifty"):

            return redirect("/admin/fifty")
        
        elif (bttn == "admin_main"):

            return redirect("/admin/main")

        elif (bttn == "admin_geofinder"):

            return redirect("/admin/geofinder")

        elif (bttn == "admin_fifty"):

            return redirect("/admin/fifty")

        elif (bttn == "admin_locations"):

            return redirect("/admin/locations")

        else:

            return redirect("/admin/locations")
        
    else:

        # Get page config from Session
        requester = session["requester"]
        active = session["get_admin_locations_content_active"]

        # Get packages from Session
        get_admin_loc_info = session["get_admin_loc_info"]
        get_admin_loc_polygon = session["get_admin_loc_polygon"]
        
        return render_template("admin_loc.html",
                               page="admin_loc", 
                               requester=requester,
                               active=active,
                               map_api_key=map_api_key,
                               get_admin_loc_info=get_admin_loc_info,
                               get_admin_loc_polygon=get_admin_loc_polygon)
        

####################################################################
# 
# ADMIN - USERS
#
####################################################################
@app.route("/admin/users", methods=["GET", "POST"])
@login_required
def admin__users():

    if request.method == "POST":

        page = request.form.get("page")
        bttn = request.form.get("bttn")

        if (bttn == "admin_user_add"):

            return redirect("/admin/user/add")
        
        elif (bttn == "admin_user"):

            # Clear Session profile messages
            session.pop("profile_message_username", None)
            session.pop("profile_message_country", None)
            session.pop("profile_message_password", None)
            
            user_id = request.form.get("user-id")

            # Set packages
            get_admin_user_header_profile = admin_users.get_admin_user_header_profile(db_pg, user_id)
            get_admin_user_header_geofinder = admin_users.get_admin_user_header_geofinder(db_pg, user_id)
            get_admin_user_header_fifty = admin_users.get_admin_user_header_fifty(db_pg, user_id)

            # Save packages to Session
            session["get_admin_user_header_profile"] = get_admin_user_header_profile
            session["get_admin_user_header_geofinder"] = get_admin_user_header_geofinder
            session["get_admin_user_header_fifty"] = get_admin_user_header_fifty

            return redirect("/admin/user")
        
        else:

            return redirect("/admin/users")
    
    else:

        # Get packages from Session
        get_admin_users_header = session["get_admin_users_header"]
        get_admin_users_content = session["get_admin_users_content"]

        return render_template("admin_users.html", 
                                page="admin_fifty", 
                                map_api_key=map_api_key,
                                get_admin_users_header=get_admin_users_header,
                                get_admin_users_content=get_admin_users_content)


####################################################################
# 
# ADMIN - USER (singlular)
#
####################################################################
@app.route("/admin/user", methods=["GET", "POST"])
@login_required
def admin__users_edit():

    if request.method == "POST":

        bttn = request.form.get("bttn")

        if (bttn == "admin_user_username"):

            username = request.form.get("username")
            user_id = request.form.get("user-id")

            if username:
                results = admin_users.get_admin_user_updated_username(db_pg, username, user_id)
                
                if results == 1:
                    session["profile_message_username"] = "Username changed"
                else:
                    session["profile_message_username"] = "Username not changed"

            # Update package
            get_admin_user_header_profile = admin_users.get_admin_user_header_profile(db_pg, user_id)

            # Save updated package to Session
            session["get_admin_user_header_profile"] = get_admin_user_header_profile

            return redirect("/admin/user")
        
        elif (bttn == "admin_user_country"):

            country = request.form.get("country")
            user_id = request.form.get("user-id")

            if country:
                results = admin_users.get_admin_user_updated_country(db_pg, country, user_id)
                
                if results == 1:
                    session["profile_message_country"] = "Country changed"
                else:
                    session["profile_message_country"] = "Country not changed"

            # Update package
            get_admin_user_header_profile = admin_users.get_admin_user_header_profile(db_pg, user_id)

            # Save updated package to Session
            session["get_admin_user_header_profile"] = get_admin_user_header_profile

            return redirect("/admin/user")

        elif (bttn == "admin_user_pass"):

            user_id = request.form.get("user_id")
            pass_new = request.form.get("pass_new")
            pass_again = request.form.get("pass_again")

            if pass_new:
                if pass_new == pass_again:
                    new_password = generate_password_hash(pass_again)
                    try:
                        admin_users.get_admin_user_updated_password(db_pg, new_password, user_id)
                        session["profile_message_password"] = "New password saved"
                    except (ValueError, RuntimeError):
                        session["profile_message_password"] = "New password not saved"
                else:
                    session["profile_message_password"] = "New password did not match"

            return redirect("/admin/user")

        else:

            return redirect("/admin/users")
    
    else:

        try:
            profile_message_username = session["profile_message_username"]
        except:
            profile_message_username = None
        
        try:
            profile_message_country = session["profile_message_country"]
        except:
            profile_message_country = None
        
        try:
            profile_message_password = session["profile_message_password"]
        except:
            profile_message_password = None

        # Get packages from Session
        get_admin_user_header_profile = session["get_admin_user_header_profile"]
        get_admin_user_header_geofinder = session["get_admin_user_header_geofinder"]
        get_admin_user_header_fifty = session["get_admin_user_header_fifty"]

        return render_template("admin_user.html", 
                                page="admin_user", 
                                map_api_key=map_api_key,
                                main=get_admin_user_header_profile,
                                header_geofinder=get_admin_user_header_geofinder,
                                header_fifty=get_admin_user_header_fifty,
                                profile_message_username=profile_message_username,
                                profile_message_country=profile_message_country,
                                profile_message_password=profile_message_password)
        

####################################################################
# 
# ADMIN - USER - ADD (aka REGISTRATION)
#
####################################################################
@app.route("/admin/user/add", methods=["GET", "POST"])
@login_required
def admin__user_add():

    if request.method == "POST":

        if session["status"] == "admin":

            # Ensure username was submitted
            if not request.form.get("username"):
                return apology("must provide username", 400)
            # Ensure password was submitted
            elif not request.form.get("password"):
                return apology("must provide password", 400)
            else:
                # Ensure password and confirmation match
                new_password = request.form.get("password")
                confirmation = request.form.get("confirmation")
                if new_password == confirmation:
                    new_username = request.form.get("username")
                    new_password = generate_password_hash(confirmation)
                    try:
                        admin_users.get_admin_user_add(db_pg, new_username, new_password)
                    except (ValueError, RuntimeError):
                        return apology("username is already taken", 400)
                    return redirect("/admin/users")
                else:
                    return apology("password did not match", 400)
        
        else:

            return redirect("/")
    
    else:

        return render_template("admin_user_add.html", 
                                map_api_key=map_api_key)
        

####################################################################
# 
# LOGIN
#
####################################################################
@app.route("/login", methods=["GET", "POST"])
def login():

    bttn = request.form.get("bttn")
    
    if request.method == "POST":

        if (bttn == "login"):

            # Clear session
            session.clear()

            # Ensure username was submitted
            if not request.form.get("username"):
                return apology("must provide username", 403)

            # Ensure password was submitted
            elif not request.form.get("password"):
                return apology("must provide password", 403)

            # Query database for username
            user = get_admin_login_user_info(db_pg, request.form.get("username"))

            # Ensure username exists and password is correct
            if user:
                if not check_password_hash(user["hash"], request.form.get("password")):
                    return apology("invalid username and/or password", 403)
            else:
                return apology("invalid username and/or password", 403)

            # Ensure user is admin
            if user["status"] != "admin":
                return apology("invalid username and/or password", 403)
            
            # Remember which user has logged in
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["status"] = user["status"]

            # Redirect user to home page
            return redirect("/")
                
        else:

            redirect ("/")
    
    else:

        # Clear session
        session.clear()

        return render_template("admin_login.html", 
                               map_api_key=map_api_key)
    

####################################################################
# 
# LOGOUT 
#
####################################################################
@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


####################################################################
# 
# ERROR 
#
####################################################################
@app.route("/error", methods=["GET", "POST"])
def error():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


#1054 #969