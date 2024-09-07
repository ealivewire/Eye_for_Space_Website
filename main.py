# PROFESSIONAL PROJECT: Space Fan Website

# OBJECTIVE: To implement a website offering users a way to get information on various points of interest pertaining to space.
# - Utilizes various technologies including Python, HTTP/REST APIs, web scraping, and database support.

# Import necessary library(ies):
import requests
from skyfield.api import load_constellation_names, position_of_radec, load_constellation_map
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Float, DateTime, func, distinct
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import unidecode
import collections  # Used for sorting items in the constellations dictionary
import xlsxwriter
from datetime import datetime, timedelta
import math
from dotenv import load_dotenv
import os
import glob
import operator

# from tkinter import messagebox

# Load environmental variables from the ".env" file:
load_dotenv()

#*** BE SURE TO CREDIT SOURCES FOR ALL DATA AVAILABLE BELOW***
# - For People In Space Now: "Data courtesy of Nathan Bergey (@natronics)"
# - For ISS location: "Data courtesy of Nathan Bergey (@natronics) and © OpenStreetMap contributors, ODbL 1.0; Reverse Geocoding courtesy of Map Maker by My Maps Inc. © Copyright 2008-2024 All Rights Reserved; Maps: @2024 Google"
# - For Mars rover data: "Data courtesy of https://github.com/chrisccerami/mars-photo-api, https://api.nasa.gov, and https://mars-photos.herokuapp.com/"
# - For Astronomy pic of the day: "Data copyrighted by Laura Rowe (Used with permission); Picture manifestation courtesy of https://apod.nasa.gov"
# - For Confirmed Planets: "This research has made use of the NASA Exoplanet Archive, which is operated by the California Institute of Technology, under contract with the National Aeronautics and Space Administration under the Exoplanet Exploration Program. Reference: DOI #10.26133/NEA12"
# - For Constellations: "Data courtesy of: 1) Skyfield, 2) © Dominic Ford 2011–2024.; Maps: GO ASTRONOMY © 2024"
# - For Space News: "Data courtesy of Spaceflight News API (SNAPI), a product by The Space Devs (TSD)"
# - For Closest Approach Asteroids: "Data is from the NASA JPL Asteroid team (http://neo.jpl.nasa.gov/); API maintained by SpaceRocks Team: David Greenfield, Arezu Sarvestani, Jason English and Peter Baunach"

# Define a constant for the URL to use in API requests for identifying people in space
# now and the spacecraft these people are on:
URL_PEOPLE_IN_SPACE_NOW = "http://api.open-notify.org/astros.json" # Free account; No limits

# Define a constant for the URL to use in API requests for identifying the current
# location of the International Space Station (ISS)":"
URL_ISS_LOCATION = "http://api.open-notify.org/iss-now" # Free account; No limits

# Define constants for the URL and API key to use in reverse-encoding the ISS latitude & longitude,
# with the purpose of yielding a human-readable address (if there is one, for the ISS can be over
# water at a particular time):
URL_GET_LOC_FROM_LAT_AND_LON = "https://geocode.maps.co/reverse"
API_KEY_GET_LOC_FROM_LAT_AND_LON = os.getenv("API_KEY_GET_LOC_FROM_LAT_AND_LON")  # Limit on free acct: 1 request/second (5,000/day)

# Define constants for the URLs and API key to use in obtaining access to summary and details re: Mars photos:
URL_MARS_ROVER_PHOTOS_BY_ROVER = "https://mars-photos.herokuapp.com/api/v1//manifests/"
URL_MARS_ROVER_PHOTOS_BY_ROVER_AND_OTHER_CRITERIA = "https://mars-photos.herokuapp.com/api/v1/rovers/"
API_KEY_MARS_ROVER_PHOTOS = os.getenv("API_KEY_MARS_ROVER_PHOTOS")  # Web Service Default Hourly Limit: 1,000 requests per hour; API Key Limits = 30 requests/IP address/hour and 50 requests/IP address/day

# Define constants for the URL and API to use in obtaining data on asteroids based on closest approach to Earth:
URL_CLOSEST_APPROACH_ASTEROIDS = "https://api.nasa.gov/neo/rest/v1/feed?"
API_KEY_CLOSEST_APPROACH_ASTEROIDS = os.getenv("API_KEY_CLOSEST_APPROACH_ASTEROIDS")

# Define constants for the URL and API key to use in API requests to yield the astronomy picture of the day:
URL_ASTRONOMY_PIC_OF_THE_DAY = "https://api.nasa.gov/planetary/apod"
API_KEY_ASTRONOMY_PIC_OF_THE_DAY = os.getenv("API_KEY_ASTRONOMY_PIC_OF_THE_DAY")

# Define constant for the URL to use in API requests to yield a listing of confirmed planets:
URL_CONFIRMED_PLANETS = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+distinct+hostname+,+sy_snum+,+sy_pnum+,+pl_name+,+disc_year+,+discoverymethod+,+disc_facility+,+disc_telescope+from+ps+where+soltype+=+'Published Confirmed'+order+by+hostname+,+pl_name+&format=json"

# Define constants for URLs pertaining to the websites which offer maps and other details for constellations:
URL_CONSTELLATION_MAP_SITE = "https://www.go-astronomy.com/constellations.htm"
URL_CONSTELLATION_ADD_DETAILS_1 = "https://in-the-sky.org/data/constellations_list.php"
URL_CONSTELLATION_ADD_DETAILS_2A = "https://in-the-sky.org/search.php?searchtype=Constellations&s=&startday=21&startmonth=7&startyear=2024&endday=30&endmonth=12&endyear=2034&ordernews=ASC&satorder=0&maxdiff=7&feed=DFAN&objorder=1&distunit=0&magmin=&magmax=&obj1Type=0&news_view=normal&distmin=&distmax=&satowner=0&satgroup=0&satdest=0&satsite=0&lyearmin=1957&lyearmax=2024&page=1"
URL_CONSTELLATION_ADD_DETAILS_2B = 'https://in-the-sky.org/search.php?searchtype=Constellations&s=&startday=21&startmonth=7&startyear=2024&endday=30&endmonth=12&endyear=2034&ordernews=ASC&satorder=0&maxdiff=7&feed=DFAN&objorder=1&distunit=0&magmin=&magmax=&obj1Type=0&news_view=normal&distmin=&distmax=&satowner=0&satgroup=0&satdest=0&satsite=0&lyearmin=1957&lyearmax=2024&page=2'

# Define constant for URL pertaining to space news:
URL_SPACE_NEWS = "https://api.spaceflightnewsapi.net/v4/articles"

# Define constant for web page loading-time allowance (in seconds) for the web-scrapers:
WEB_LOADING_TIME_ALLOWANCE = 5


# Initialize the Flask app. object
app = Flask(__name__)


# Create needed class "Base":
class Base(DeclarativeBase):
  pass


# Configure the SQLite database, relative to the app instance folder:
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///space.db"

# Initialize an instance of Bootstrap5, using the "app" object defined above as a parameter:
Bootstrap5(app)

# Retrieve the secret key to be used for CSRF protection:
app.secret_key = os.getenv("SECRET_KEY_FOR_CSRF_PROTECTION")

# Create the db object using the SQLAlchemy constructor:
db = SQLAlchemy(model_class=Base)

# Initialize the app with the extension:
db.init_app(app)

# Define list variable for storing names of Mars rovers that are currently active for the purpose of data production:
mars_rovers = []


# CONFIGURE DATABASE TABLES (LISTED IN ALPHABETICAL ORDER):
class ApproachingAsteroids(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    absolute_magnitude_h: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_diameter_km_min: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_diameter_km_max: Mapped[float] = mapped_column(Float, nullable=False)
    is_potentially_hazardous: Mapped[bool] = mapped_column(Boolean, nullable=False)
    close_approach_date: Mapped[str] = mapped_column(String(10), nullable=False)
    relative_velocity_km_per_s: Mapped[float] = mapped_column(Float, nullable=False)
    miss_distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    orbiting_body: Mapped[str] = mapped_column(String(20), nullable=False)
    is_sentry_object: Mapped[bool] = mapped_column(Boolean, nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)


class ConfirmedPlanets(db.Model):
    row_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    host_name: Mapped[str] = mapped_column(String(50), nullable=False)
    host_num_stars: Mapped[int] = mapped_column(Integer, nullable=False)
    host_num_planets: Mapped[int] = mapped_column(Integer, nullable=False)
    planet_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    discovery_year: Mapped[int] = mapped_column(Integer, nullable=False)
    discovery_method: Mapped[str] = mapped_column(String(50), nullable=False)
    discovery_facility: Mapped[str] = mapped_column(String(100), nullable=False)
    discovery_telescope: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)


class Constellations(db.Model):
    row_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[int] = mapped_column(String(20), unique=True, nullable=False)
    abbreviation: Mapped[str] = mapped_column(String(10), unique=False, nullable=False)
    nickname: Mapped[str] = mapped_column(String(30), unique=False, nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    area: Mapped[str] = mapped_column(String(50), unique=False, nullable=False)
    myth_assoc: Mapped[str] = mapped_column(String(500), unique=False, nullable=False)
    first_appear: Mapped[str] = mapped_column(String(50), unique=False, nullable=False)
    brightest_star_name: Mapped[str] = mapped_column(String(40), unique=False, nullable=False)
    brightest_star_url: Mapped[str] = mapped_column(String(40), unique=False, nullable=False)


class MarsPhotoDetails(db.Model):
    row_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rover_earth_date_combo = mapped_column(String(32), nullable=False)
    rover_name: Mapped[str] = mapped_column(String(15), nullable=False)
    sol: Mapped[str] = mapped_column(String(15), unique=False, nullable=False)
    pic_id: Mapped[int] = mapped_column(Integer, nullable=False)
    earth_date: Mapped[str] = mapped_column(String(15), nullable=False)
    camera_name: Mapped[str] = mapped_column(String(20), nullable=False)
    camera_full_name: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)


class MarsPhotosAvailable(db.Model):
    row_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rover_earth_date_combo = mapped_column(String(32), nullable=False)
    rover_name: Mapped[str] = mapped_column(String(15), nullable=False)
    sol: Mapped[str] = mapped_column(String(15), unique=False, nullable=False)
    earth_date: Mapped[str] = mapped_column(String(15), nullable=False)
    cameras: Mapped[str] = mapped_column(String(250), nullable=False)
    total_photos: Mapped[int] = mapped_column(Integer, nullable=False)


class MarsRoverCameras(db.Model):
    row_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rover_name: Mapped[str] = mapped_column(String(15), nullable=False)
    camera_name: Mapped[str] = mapped_column(String(20), nullable=False)
    camera_full_name: Mapped[str] = mapped_column(String(50), nullable=False)


class MarsRovers(db.Model):
    row_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rover_name: Mapped[str] = mapped_column(String(15), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)


class SpaceNews(db.Model):
    row_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int] = mapped_column(Integer, nullable=False)
    news_site: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    date_time_published: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    date_time_updated: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)


# CONFIGURE FORMS FOR USE IN HTML FILES (LISTED IN ALPHABETICAL ORDER):
# Configure form for viewing "approaching asteroids" spreadsheet:
class DisplayApproachingAsteroidsSheetForm(FlaskForm):
    list_approaching_asteroids_sheet_name = SelectField("Approaching Asteroids Sheet:", choices=[], validate_choice=False)
    button_submit = SubmitField(label="View Approaching Asteroids Spreadsheet")


# Configure form for viewing "confirmed planets" spreadsheet:
class DisplayConfirmedPlanetsSheetForm(FlaskForm):
    list_confirmed_planets_sheet_name = SelectField("Confirmed Planets Sheet:", choices=[], validate_choice=False)
    button_submit = SubmitField(label="View Confirmed Planets Spreadsheet")


# Configure form for viewing "constellations" spreadsheet:
class DisplayConstellationSheetForm(FlaskForm):
    list_constellation_sheet_name = SelectField("Constellation Sheet:", choices=[], validate_choice=False)
    button_submit = SubmitField(label="View Constellations Spreadsheet")


# Configure form for viewing "Mars photos" spreadsheet (summary or detailed):
class DisplayMarsPhotosSheetForm(FlaskForm):
    list_mars_photos_sheet_name = SelectField("Mars Photos Sheet:", choices=[], validate_choice=False)
    button_submit = SubmitField(label="View Mars Photos Spreadsheet")


# Configure form for viewing "approaching asteroids" data online (on dedicated web page):
class ViewApproachingAsteroidsForm(FlaskForm):
    list_close_approach_date = SelectField("Select Close Approach Date:", choices=[], validate_choice=False)
    button_submit = SubmitField(label="View Details")


# Configure form for viewing "confirmed planets" data online (on dedicated web page):
class ViewConfirmedPlanetsForm(FlaskForm):
    list_discovery_year = SelectField("Select Discovery Year:", choices=[], validate_choice=False)
    button_submit = SubmitField(label="View List of Confirmed Planets")


# Configure form for viewing "constellations" data online (on dedicated web page):
class ViewConstellationForm(FlaskForm):
    list_constellation_name = SelectField("Select Constellation Name:", choices=[], validate_choice=False)
    button_submit = SubmitField(label="View Details")


# Configure form for viewing "Mars photos" data online (on dedicated web page):
class ViewMarsPhotosForm(FlaskForm):
    list_rover_name = SelectField("Select Rover Name:", choices=[], validate_choice=False)
    list_earth_date = SelectField("Select Earth Date:", choices=[], validate_choice=False)
    button_submit = SubmitField(label="View List of Photos")


# If needed tables do not already exist in the DB, create them:
with app.app_context():
    db.create_all()


# CONFIGURE ROUTES FOR WEB PAGES (LISTED IN HIERARCHICAL ORDER STARTING WITH HOME PAGE, THEN ALPHABETICALLY):
# Configure route for home page:
@app.route('/')
def home():
    global db, app

    return render_template("index.html")


# Configure route for "About" web page:
@app.route('/about')
def about():
    global db, app

    return render_template("about.html")


# Configure route for "Administration" web page:
@app.route('/admin_for_website')
def admin_for_website():
    global db, app

    run_apis()

    # Go to the admin web page:
    return render_template("about.html")


# Configure route for "Approaching Asteroids" web page:
@app.route('/approaching_asteroids',methods=["GET", "POST"])
def approaching_asteroids():
    global db, app

    # Instantiate an instance of the "ViewApproachingAsteroidsForm" class:
    form = ViewApproachingAsteroidsForm()

    # Instantiate an instance of the "DisplayApproachingAsteroidsSheetForm" class:
    form_ss = DisplayApproachingAsteroidsSheetForm()

    # Populate the close approach date listbox with an ordered list of close approach dates represented in the database:
    list_close_approach_dates = []
    close_approach_dates = db.session.query(distinct(ApproachingAsteroids.close_approach_date)).order_by(ApproachingAsteroids.close_approach_date).all()
    for close_approach_date in close_approach_dates:
        list_close_approach_dates.append(str(close_approach_date)[2:12])
    form.list_close_approach_date.choices = list_close_approach_dates

    # Populate the approaching-asteroids sheet file listbox with the sole sheet viewable in this scope:
    form_ss.list_approaching_asteroids_sheet_name.choices = ["ApproachingAsteroids.xlsx"]

    # Validate form entries upon submittal. Depending on the form involved, perform additional processing:
    if form.validate_on_submit():
        if form.list_close_approach_date.data != None:
            error_msg = ""
            # Retrieve the record from the database which pertains to confirmed planets discovered in the selected year:
            approaching_asteroids_details = retrieve_from_database(trans_type="approaching_asteroids_by_close_approach_date", close_approach_date=form.list_close_approach_date.data)

            if approaching_asteroids_details == {}:
                error_msg = "Error: Data could not be obtained at this time."
            elif approaching_asteroids_details == []:
                error_msg = "No matching records were retrieved."

            # Show web page with retrieved approaching-asteroid details:
            return render_template('show_approaching_asteroids_details.html', approaching_asteroids_details=approaching_asteroids_details, close_approach_date=form.list_close_approach_date.data, error_msg=error_msg)

        else:
            # Open the selected spreadsheet file:
            os.startfile(str(form_ss.list_approaching_asteroids_sheet_name.data))

    # Go to the web page to render the results:
    return render_template('approaching_asteroids.html', form=form, form_ss=form_ss)


# Configure route for "Astronomy Pic of the Day" web page:
@app.route('/astronomy_pic_of_day')
def astronomy_pic_of_day():
    global db, app

    # Get details re: the astronomy picture of the day:
    json, copyright_details, error_msg = get_astronomy_pic_of_the_day()

    # Go to the web page to render the results:
    return render_template("astronomy_pic_of_day.html", json=json, copyright_details=copyright_details, error_msg=error_msg)


# Configure route for "Confirmed Planets" web page:
@app.route('/confirmed_planets',methods=["GET", "POST"])
def confirmed_planets():
    global db, app

    # Instantiate an instance of the "ViewConstellationForm" class:
    form = ViewConfirmedPlanetsForm()

    # Instantiate an instance of the "DisplayConfirmedPlanetsSheetForm" class:
    form_ss = DisplayConfirmedPlanetsSheetForm()

    # Populate the discovery year listbox with an ordered (descending) list of discovery years represented in the database:
    list_discovery_years = []
    discovery_years = db.session.query(distinct(ConfirmedPlanets.discovery_year)).order_by(ConfirmedPlanets.discovery_year.desc()).all()
    for year in discovery_years:
        list_discovery_years.append(int(str(year)[1:5]))
    form.list_discovery_year.choices = list_discovery_years

    # Populate the confirmed planets sheet file listbox with the sole sheet viewable in this scope:
    form_ss.list_confirmed_planets_sheet_name.choices = ["ConfirmedPlanets.xlsx"]

    # Validate form entries upon submittal. Depending on the form involved, perform additional processing:
    if form.validate_on_submit():
        if form.list_discovery_year.data != None:
            error_msg = ""
            # Retrieve the record from the database which pertains to confirmed planets discovered in the selected year:
            confirmed_planets_details = retrieve_from_database(trans_type="confirmed_planets_by_disc_year", disc_year=form.list_discovery_year.data)

            if confirmed_planets_details == {}:
                error_msg = "Error: Data could not be obtained at this time."
            elif confirmed_planets_details == []:
                error_msg = "No matching records were retrieved."

            # Show web page with retrieved confirmed-planet details:
            return render_template('show_confirmed_planets_details.html', confirmed_planets_details=confirmed_planets_details, disc_year=form.list_discovery_year.data, error_msg=error_msg)

        else:
            # Open the selected spreadsheet file:
            os.startfile(str(form_ss.list_confirmed_planets_sheet_name.data))

    return render_template('confirmed_planets.html', form=form, form_ss=form_ss)


# Configure route for "Constellations" web page:
@app.route('/constellations',methods=["GET", "POST"])
def constellations():
    global db, app

    # Instantiate an instance of the "ViewConstellationForm" class:
    form = ViewConstellationForm()

    # Instantiate an instance of the "DisplayConstellationSheetForm" class:
    form_ss = DisplayConstellationSheetForm()

    # Populate the constellation name listbox with an ordered list of constellation names from the database:
    form.list_constellation_name.choices = db.session.execute(db.select(Constellations.name + " (" + Constellations.nickname + ")").order_by(Constellations.name)).scalars().all()

    # Populate the constellation sheet file listbox with the sole sheet viewable in this scope:
    form_ss.list_constellation_sheet_name.choices = ["Constellations.xlsx"]

    # Validate form entries upon submittal. Depending on the form involved, perform additional processing:
    if form.validate_on_submit():

        if form.list_constellation_name.data != None:
            # Capture selected constellation name:
            selected_constellation_name = form.list_constellation_name.data.split("(")[0][:len(form.list_constellation_name.data.split("(")[0])-1]

            # Retrieve the record from the database which pertains to the selected constellation name:
            constellation_details = db.session.execute(db.select(Constellations).where(Constellations.name == selected_constellation_name)).scalar()

            # Show web page with retrieved constellation details:
            return render_template('show_constellation_details.html', constellation_details=constellation_details)

        else:
            # Open the selected spreadsheet file:
            os.startfile(str(form_ss.list_constellation_sheet_name.data))

    return render_template('constellations.html', form=form, form_ss=form_ss)


# Configure route for "Photos from Mars" web page:
@app.route('/mars_photos',methods=["GET", "POST"])
def mars_photos():
    global db, app

    # Instantiate an instance of the "ViewConstellationForm" class:
    form = ViewMarsPhotosForm()

    # Instantiate an instance of the "DisplayMarsPhotosSheetForm" class:
    form_ss = DisplayMarsPhotosSheetForm()

    # Populate the rover name listbox with an ordered of active rover names:
    form.list_rover_name.choices = db.session.execute(db.select(MarsRovers.rover_name).where(MarsRovers.active == "Yes").order_by(MarsRovers.rover_name)).scalars().all()

    # Populate the earth date listbox with an ordered of earth dates where the selected rover has produced photos:
    form.list_earth_date.choices = db.session.query(distinct(MarsPhotosAvailable.earth_date)).where(MarsPhotosAvailable.rover_name == form.list_rover_name.data).order_by(MarsPhotosAvailable.earth_date.desc()).all()

    # list_discovery_years = []
    # discovery_years = db.session.query(distinct(ConfirmedPlanets.discovery_year)).order_by(ConfirmedPlanets.discovery_year.desc()).all()
    # for year in discovery_years:
    #     list_discovery_years.append(int(str(year)[1:5]))
    # form.list_discovery_year.choices = list_discovery_years

    # Populate the Mars photos sheet file listbox with all filenames of spreadsheets pertinent to this scope:
    form_ss.list_mars_photos_sheet_name.choices = glob.glob("Mars Photos*.xlsx")

    # Validate form entries upon submittal. Depending on the form involved, perform additional processing:
    if form.validate_on_submit():
        if form.list_discovery_year.data != None:
            error_msg = ""
            # Retrieve the record from the database which pertains to confirmed planets discovered in the selected year:
            confirmed_planets_details = retrieve_from_database(trans_type="confirmed_planets_by_disc_year", disc_year=form.list_discovery_year.data)

            if confirmed_planets_details == {}:
                error_msg = "Error: Data could not be obtained at this time."
            elif confirmed_planets_details == []:
                error_msg = "No matching records were retrieved."

            # Show web page with retrieved constellation details:
            return render_template('show_confirmed_planets_details.html', confirmed_planets_details=confirmed_planets_details, disc_year=form.list_discovery_year.data, error_msg=error_msg)

        else:
            # Open the selected spreadsheet file:
            os.startfile(str(form_ss.list_mars_photos_sheet_name.data))

    return render_template('mars_photos.html', form=form, form_ss=form_ss)


# Configure route for "Space News" web page:
@app.route('/space_news')
def space_news():
    global db, app

    # Get results of obtaining and processing the desired information:
    success, error_msg = get_space_news()

    if success:
        # Query the table for space news articles:
        with app.app_context():
            articles = db.session.execute(db.select(SpaceNews).order_by(SpaceNews.row_id)).scalars().all()
            # articles = db.session.execute(db.select(SpaceNews.row_id, SpaceNews.title, SpaceNews.news_site, SpaceNews.summary, datetime.strptime(str(SpaceNews.date_time_published), "%d-%b-%Y %H:%M:%S"), datetime.strptime(str(SpaceNews.date_time_updated), "%d-%b-%Y %H:%M:%S"), SpaceNews.date_time_updated, SpaceNews.url).order_by(SpaceNews.row_id)).scalars().all()
            # articles = db.session.execute(db.select(SpaceNews.row_id, SpaceNews.title, SpaceNews.news_site, SpaceNews.summary, SpaceNews.date_time_published, SpaceNews.date_time_updated, SpaceNews.url).order_by(SpaceNews.row_id)).scalars().all()
            # print(articles)
            if articles.count == 0:
                success = False
                error_msg = "Error: Cannot retrieve article data from database."

    else:
        articles = None

    # Go to the web page to render the results:
    return render_template("space_news.html", articles=articles, success=success, error_msg=error_msg)


# Configure route for "Where is ISS" web page:
@app.route('/where_is_iss')
def where_is_iss():
    global db, app

    # Get ISS's current location along with a URL to get a map plotting said location:
    location_address, location_url = get_iss_location()

    # Go to the web page to render the results:
    return render_template("where_is_iss.html", location_address=location_address, location_url=location_url, has_url=not(location_url == ""))


# Configure route for "Who is in Space Now" web page:
@app.route('/who_is_in_space_now')
def who_is_in_space_now():
    global db, app

    # Get results of obtaining a JSON with the desired information:
    json, has_json = get_people_in_space_now()

    # Go to the web page to render the results:
    return render_template("who_is_in_space_now.html", json=json, has_json=has_json)


# DEFINE FUNCTIONS TO BE USED FOR THIS APPLICATION (LISTED IN ALPHABETICAL ORDER BY FUNCTION NAME):
def close_workbook(workbook):
    """Function to close a spreadsheet workbook, checking if the file is open"""
    while True:
        try:
            workbook.close()

        except xlsxwriter.exceptions.FileCreateError as e:
            user_answer = input("Exception caught in workbook.close(): %s\n"
                                "Please close the file if it is open in Excel.\n"
                                "Try to write file again? (y/n|): " % e
                                )
            if user_answer.lower() != "n":
                continue
        break


def create_workbook(workbook_name):
    """Function for creating and returning a spreadsheet workbook for subsequent population/formatting"""
    # Create and return the workbook:
    return xlsxwriter.Workbook(workbook_name)


def create_worksheet(workbook, worksheet_name):
    """Function for creating and returning a spreadsheet worksheet for subsequent population/formatting"""
    # Create and return the worksheet:
    return workbook.add_worksheet(worksheet_name)


def export_approaching_asteroids_data_to_spreadsheet(approaching_asteroids_data):
    """Function to export approaching-asteroids data to a spreadsheet, with all appropriate formatting applied"""
    try:
        # Capture current date/time:
        current_date_time = datetime.now()
        current_date_time_spreadsheet = current_date_time.strftime("%d-%b-%Y @ %I:%M %p")

        # Create the workbook:
        approaching_asteroids_workbook = create_workbook(f"ApproachingAsteroids.xlsx")

        # Create the worksheet to contain approaching-asteroids data from the "approaching_asteroids_data" variable:
        approaching_asteroids_worksheet = create_worksheet(approaching_asteroids_workbook, "Approaching Asteroids")

        # Add and format the column headers:
        prepare_spreadsheet_main_contents(approaching_asteroids_workbook, approaching_asteroids_worksheet, "approaching_asteroids_headers")

        # Iterate through the "approaching_asteroids_data" variable and write/format each asteroid's data into the worksheet:
        prepare_spreadsheet_main_contents(approaching_asteroids_workbook, approaching_asteroids_worksheet, "approaching_asteroids_data", list_name=approaching_asteroids_data)

        # Add and format the spreadsheet header row, and implement the following: column widths, footer, page orientation, and margins:
        prepare_spreadsheet_supplemental_formatting(approaching_asteroids_workbook, approaching_asteroids_worksheet, "approaching_asteroids", current_date_time_spreadsheet, approaching_asteroids_data, 11, (12, 20, 10, 15, 15, 15, 15, 12, 12, 10, 10, 65) )

        # Close the workbook, checking if the file is open:
        close_workbook(approaching_asteroids_workbook)

        # Return successful-execution indication to the calling function:
        return True

    except Exception as err:  # An error has occurred.
        # Print error message:
        print(f"Error (Export Approaching Asteroids Data to SS: {err}")

        # Return failed-execution indication to the calling function:
        return False


def export_confirmed_planets_data_to_spreadsheet(confirmed_planets_data):
    """Function to export confirmed-planet data to a spreadsheet, with all appropriate formatting applied"""
    try:
        # Capture current date/time:
        current_date_time = datetime.now()
        current_date_time_spreadsheet = current_date_time.strftime("%d-%b-%Y @ %I:%M %p")

        # Create the workbook:
        confirmed_planets_workbook = create_workbook(f"ConfirmedPlanets.xlsx")

        # Create the worksheet to contain confirmed-planet data from the "confirmed_planets_data" variable:
        confirmed_planets_worksheet = create_worksheet(confirmed_planets_workbook, "Confirmed Planets")

        # Add and format the column headers:
        prepare_spreadsheet_main_contents(confirmed_planets_workbook, confirmed_planets_worksheet, "confirmed_planets_headers")

        # Iterate through the "confirmed_planets_data" variable and write/format each planet's data into the worksheet:
        prepare_spreadsheet_main_contents(confirmed_planets_workbook, confirmed_planets_worksheet, "confirmed_planets_data", list_name=confirmed_planets_data)

        # Add and format the spreadsheet header row, and implement the following: column widths, footer, page orientation, and margins:
        prepare_spreadsheet_supplemental_formatting(confirmed_planets_workbook, confirmed_planets_worksheet, "confirmed_planets", current_date_time_spreadsheet, confirmed_planets_data, 8, (15, 10, 10, 15, 10, 15, 30, 20, 65) )

        # Close the workbook, checking if the file is open:
        close_workbook(confirmed_planets_workbook)

        # Return successful-execution indication to the calling function:
        return True

    except Exception as err:  # An error has occurred.
        # Print error message:
        print(f"Error (Export Confirmed Planets Data to SS: {err}")

        # Return failed-execution indication to the calling function:
        return False


def export_constellation_data_to_spreadsheet(constellations_data):
    """Function to export constellation data to a spreadsheet, with all appropriate formatting applied"""
    try:
        # Capture current date/time:
        current_date_time = datetime.now()
        current_date_time_spreadsheet = current_date_time.strftime("%d-%b-%Y @ %I:%M %p")

        # Create the workbook:
        constellation_workbook = create_workbook(f"Constellations.xlsx")

        # Create the worksheet to contain constellation data from the "constellation_data" variable:
        constellation_worksheet = create_worksheet(constellation_workbook, "Constellations")

        # Add and format the column headers:
        prepare_spreadsheet_main_contents(constellation_workbook, constellation_worksheet, "constellation_headers")

        # Iterate through the "constellation_data" variable and write/format each constellation's data into the worksheet:
        i = 3
        for key in constellations_data:
            prepare_spreadsheet_main_contents(constellation_workbook, constellation_worksheet, "constellation_data", dict_name=constellations_data, key=key, i=i)
            i += 1

        # Add and format the spreadsheet header row, and implement the following: column widths, footer, page orientation, and margins:
        prepare_spreadsheet_supplemental_formatting(constellation_workbook, constellation_worksheet, "constellations", current_date_time_spreadsheet, constellations_data, 7, (15, 7.8, 15, 75, 15, 20, 15, 53) )

        # Close the workbook, checking if the file is open:
        close_workbook(constellation_workbook)

        # Return successful-execution indication to the calling function:
        return True

    except Exception as err:  # An error has occurred.
        # Print error message:
        print(f"Error (Export Constellation Data to SS: {err}")

        # Return failed-execution indication to the calling function:
        return False


def export_mars_photos_to_spreadsheet(photos_available, photo_details):
    """Function to export data on available Mars rover photos to a spreadsheet, with all appropriate formatting applied"""
    try:
        # Inform user that export-to-spreadsheet execution will begin:
        print("Mars photos: Exporting results to spreadsheet file...")

        # Capture current date/time:
        current_date_time = datetime.now()
        current_date_time_spreadsheet = current_date_time.strftime("%d-%b-%Y @ %I:%M %p")

        # Create the workbook:
        photos_available_workbook = xlsxwriter.Workbook(f"Mars Photos - Summary.xlsx")

        # Create the worksheet to contain photos-available data from the "photos_available" list of database records:
        photos_available_worksheet = create_worksheet(photos_available_workbook, f"Summary")

        # Add and format the column headers:
        prepare_spreadsheet_main_contents(photos_available_workbook, photos_available_worksheet, "photos_available_headers")

        # Populate the "Photo Summary" worksheet with the contents of the "photos_available" list of database records:
        prepare_spreadsheet_main_contents(photos_available_workbook, photos_available_worksheet,"photos_available_data", list_name=photos_available)

        # Add and format the spreadsheet header row, and implement the following: column widths, footer, page orientation, and margins:
        prepare_spreadsheet_supplemental_formatting(photos_available_workbook, photos_available_worksheet, "photos_available", current_date_time_spreadsheet, photos_available, 4, (15, 15, 7, 80, 15))

        # Close the workbook, checking if the file is open:
        print(f"Mars photos: Spreadsheet file 'Mars Photos - Summary.xlsx': Saving in progress...")
        close_workbook(photos_available_workbook)
        print(f"Mars photos: Spreadsheet file 'Mars Photos - Summary.xlsx': Saving completed...")

        # For each rover, create and format a worksheet to contain details for available photos
        # taken by that rover each earth year:
        rovers_represented = []
        rovers_represented = get_mars_photos_summarize_photo_counts_by_rover_and_earth_year()
        if rovers_represented == []:
            exit()

        print(rovers_represented)
        # print(len(rovers_represented))

        # rovers_represented[1] = ('Opportunity', 30000)

        worksheets_needed = []
        row_start = 0
        row_end = 0
        for i in range(0, len(rovers_represented)):
            rover_name = rovers_represented[i][0]
            earth_year = rovers_represented[i][1]
            rover_earth_year_combo = rovers_represented[i][2]
            if rovers_represented[i][3] <= 65530:
                row_end += rovers_represented[i][3]
                worksheets_needed.append((rover_earth_year_combo, earth_year, rover_name, 1, row_start, row_end))
                row_start = row_end
            else:
                worksheet_to_add = ""
                rover_number_of_sheets_needed = math.ceil(rovers_represented[i][3] / 65530)

                for j in range(0, rover_number_of_sheets_needed):
                    worksheet_to_add = rover_earth_year_combo + "_Part" + str(j + 1)
                    if (j + 1) == rover_number_of_sheets_needed:
                        row_end += rovers_represented[i][3] - 65530
                    else:
                        row_end += 65530
                    worksheets_needed.append((worksheet_to_add, earth_year, rover_name, rover_number_of_sheets_needed, row_start, row_end))
                    row_start = row_end

        # for item in worksheets_needed:
        #     print(item)
        print(worksheets_needed)
        # print(len(worksheets_needed))

        # exit()

        for i in range(0, len(worksheets_needed)):
            # Create the workbook:
            photo_details_workbook = xlsxwriter.Workbook(f"Mars Photos - Details - {worksheets_needed[i][0]}.xlsx")

            # Create the worksheet to contain photo-details data from the "photo_details" list of database records:
            # photo_details_worksheet = create_worksheet(photo_details_workbook, worksheets_needed[i][0])
            photo_details_worksheet = create_worksheet(photo_details_workbook, "Details")

            # Add and format the column headers:
            prepare_spreadsheet_main_contents(photo_details_workbook, photo_details_worksheet,"photo_details_headers")

            # Populate the worksheet with its corresponding contents of the "photo_details" list of database records:
            prepare_spreadsheet_main_contents(photo_details_workbook, photo_details_worksheet, "photo_details_data", list_name=photo_details, worksheet_details=worksheets_needed[i])

            # Add and format the spreadsheet header row, and implement the following: column widths, footer, page orientation, and margins:
            prepare_spreadsheet_supplemental_formatting(photo_details_workbook, photo_details_worksheet, "photo_details", current_date_time_spreadsheet, photos_available, 4, (15, 15, 7, 15, 30, 50, 80), rover_name=worksheets_needed[i][2], earth_year=worksheets_needed[i][1], rover_earth_year_combo=worksheets_needed[i][0], rover_number_of_sheets_needed=worksheets_needed[i][3])

            # Close the workbook, checking if the file is open:
            print(f"Mars photos: Spreadsheet file 'Mars Photos - Details - {worksheets_needed[i][0]}.xlsx': Saving in progress...")
            close_workbook(photo_details_workbook)
            print(f"Mars photos: Spreadsheet file 'Mars Photos - Details - {worksheets_needed[i][0]}.xlsx': Saving completed.")

        # Return successful-execution indication to the calling function:
        return True

    except Exception as err:  # An error has occurred.
        # Print error message:
        print(f"Error (Export Mars rover photos data to SS): {err}")

        # Return failed-execution indication to the calling function:
        return False


def find_element(driver, find_type, find_details):
    """Function to find an element via a web-scraping procedure"""
    if find_type == "xpath":
        return driver.find_element(By.XPATH, find_details)


def get_confirmed_planets():
    """Function for getting all needed data pertaining to confirmed planets and store such information in the space database supporting our website"""
    try:
        # Execute API request:
        response = requests.get(URL_CONFIRMED_PLANETS)
        if response.status_code == 200:
            # Delete the existing records in the "confirmed_planets" database table:
            if not update_database("update_confirmed_planets_delete_existing", {}):
                exit()

            # Import the up-to-date data (from the JSON) into the "confirmed_planets" database table.
            # NOTE:  Scope of data: Solution Type = 'Published Confirmed'
            if not update_database("update_confirmed_planets_import_new", response.json()):
                exit()

            # Retrieve all existing records in the "confirmed_planets" database table. If the function
            # called returns an empty directory, end this procedure:
            confirmed_planets_data = retrieve_from_database("confirmed_planets")
            if confirmed_planets_data == {}:
                exit()

            # Create and format a spreadsheet file (workbook) to contain all confirmed-planet data. If the function called returns an empty directory, end this procedure:
            if not export_confirmed_planets_data_to_spreadsheet(confirmed_planets_data):
                exit()

    except Exception as err:
        print(f"Error (Confirmed Planets): {err}")


def get_constellation_data():
    """Function for getting all needed data pertaining to constellations and store such information in the space database supporting our website"""

    # Obtain a list of constellation using the skyfield.api library:
    constellations = dict(load_constellation_names())

    # If a constellation list has been obtained:
    if constellations != {}:
        try:
            # Get the nicknames for each constellation identified.  If the function called returns an empty directory, end this procedure:
            constellations_data = get_constellation_data_nicknames(constellations)
            if constellations_data == {}:
                exit()
                
            # Get additional details for each constellation identified.  If the function called returns an empty directory, end this procedure:
            constellations_added_details = get_constellation_data_added_details(constellations)
            if constellations_added_details == {}:
                exit()

            # Get additional details for each constellation identified.  If the function called returns an empty directory, end this procedure:
            constellations_area = get_constellation_data_area(constellations)
            if constellations_area == {}:
                exit()

            # Add the additional details (including area) to the main constellation dictionary:
            for key in constellations_data:
                constellations_data[key]["area"] = constellations_area[key]["area"]
                constellations_data[key]["myth_assoc"] = constellations_added_details[key]["myth_assoc"]
                constellations_data[key]["first_appear"] = constellations_added_details[key]["first_appear"]
                constellations_data[key]["brightest_star_name"] = constellations_added_details[key]["brightest_star_name"]
                constellations_data[key]["brightest_star_url"] = constellations_added_details[key]["brightest_star_url"]

            # Delete the existing records in the "constellations" database table and update same with the
            # contents of the "constellations_data" dictionary.  If the function called returns a failed-execution
            # indication, end this procedure:
            if not update_database("update_constellations", constellations_data):
                exit()

            # Retrieve all existing records in the "constellations" database table. If the function
            # called returns an empty directory, end this procedure:
            constellations_data = retrieve_from_database("constellations")
            if constellations_data == {}:
                exit()

            # Create and format a spreadsheet file (workbook) to contain all constellation data. If the function called returns an empty directory, end this procedure:
            if not export_constellation_data_to_spreadsheet(constellations_data):
                exit()

        except Exception as err:
            print(f"Error (Constellation Data): {err}")

    else:  # An error has occurred in processing constellation data.
        print("Error: Data for 'Constellations' cannot be obtained at this time.")


def get_constellation_data_added_details(constellations):
    """Function for getting (via web-scraping) additional details for each constellation identified"""
    # Define a variable for storing the additional details for each constellation (to be scraped from the constellation map website):
    constellations_added_details = {}

    # Constellation "Serpens" is represented via 2 separate entries in the target website (head & tail). Accordingly, define variables to be used
    # as part of the workaround to handle this constellation's data differently than the rest:
    serpens_element_constellation_myth_assoc_text = ""
    serpens_element_constellation_first_appear_text = ""
    serpens_element_constellation_brightest_star_text = ""
    serpens_element_constellation_brightest_star_url = ""
    
    try:
        # Initiate and configure a Selenium object to be used for scraping website for additional constellation details:
        driver = setup_selenium_driver(URL_CONSTELLATION_ADD_DETAILS_1, 1, 1)

        # Pause program execution to allow for constellation website loading time:
        time.sleep(WEB_LOADING_TIME_ALLOWANCE)

        # Define special variables to handle the 'Serpens' constellation whose data spans 2 entries (head/tail) on the target website:
        serpens_index = 0
        serpens_list = ["Head: ", "Tail: "]

        # Scrape the constellation map website to obtain additional details for each constellation:
        for i in range(1, len(constellations) + 1 + 1):  # Added 1 because the constellation "Serpens" is rep'd by two separate entries on this website
            # Find the element pertaining to the constellation's name. Decode it to normalize to ASCII-based characters:
            element_constellation_name = find_element(driver, "xpath", '/html/body/div/div[3]/div[1]/div[1]/div/div[3]/div[2]/table/tbody/tr[' + str(i) + ']/td[1]/a')
            element_constellation_name_unidecoded = unidecode.unidecode(element_constellation_name.get_attribute("text"))

            # Find the element pertaining to the constellation's mythological association:
            element_constellation_myth_assoc = find_element(driver, "xpath", '/html/body/div/div[3]/div[1]/div[1]/div/div[3]/div[2]/table/tbody/tr[' + str(i) + ']/td[2]/div')
            element_constellation_myth_assoc_text = element_constellation_myth_assoc.get_attribute("innerHTML")

            # Find the element pertaining to the constellation's first appearance:
            element_constellation_first_appear = find_element(driver, "xpath", '/html/body/div/div[3]/div[1]/div[1]/div/div[3]/div[2]/table/tbody/tr[' + str(i) + ']/td[3]/div')
            element_constellation_first_appear_text = element_constellation_first_appear.get_attribute("innerHTML")

            # Find the element pertaining to the constellation's brightest star.  Capture both text and url:
            element_constellation_brightest_star = find_element(driver, "xpath", '/html/body/div/div[3]/div[1]/div[1]/div/div[3]/div[2]/table/tbody/tr[' + str(i) + ']/td[5]/a')
            element_constellation_brightest_star_text = element_constellation_brightest_star.get_attribute("text").replace(" ", "").replace("\n", "")
            element_constellation_brightest_star_url = element_constellation_brightest_star.get_attribute("href")

            # Add the additional details collected above to the "constellation added details" dictionary:
            if "Serpens" in element_constellation_name_unidecoded:  # Constellation "Serpens" is represented via 2 separate entries in the target website (head & tail).
                serpens_element_constellation_myth_assoc_text += serpens_list[serpens_index] + element_constellation_myth_assoc_text + " "
                serpens_element_constellation_first_appear_text += serpens_list[serpens_index] + element_constellation_first_appear_text + " "
                serpens_element_constellation_brightest_star_text += serpens_list[serpens_index] + element_constellation_brightest_star_text + " "
                serpens_element_constellation_brightest_star_url += element_constellation_brightest_star_url + " "

                constellations_added_details["Serpens"] = {
                    "myth_assoc": serpens_element_constellation_myth_assoc_text,
                    "first_appear": serpens_element_constellation_first_appear_text,
                    "brightest_star_name": serpens_element_constellation_brightest_star_text,
                    "brightest_star_url": serpens_element_constellation_brightest_star_url
                }

                serpens_index += 1

            else:
                constellations_added_details[element_constellation_name_unidecoded] = {
                    "myth_assoc": element_constellation_myth_assoc_text,
                    "first_appear": element_constellation_first_appear_text,
                    "brightest_star_name": element_constellation_brightest_star_text,
                    "brightest_star_url": element_constellation_brightest_star_url
                }

        # Sort the "constellation added details" dictionary in alphabetical order by its key (the constellation's name):
        constellations_added_details = collections.OrderedDict(sorted(constellations_added_details.items()))

        # Close and delete the Selenium driver object:
        driver.close()
        del driver

        # Return the populated "constellations_added_details" dictionary to the calling function:
        return constellations_added_details

    except Exception as err:  # An error has occurred.
        # Print error message:
        print(f"Error (Constellation Data - Added Details): {err}")

        # Return empty directory as a failed-execution indication to the calling function:
        return {}


def get_constellation_data_area(constellations):
    """Function for getting (via web-scraping) the area for each constellation identified"""
    # Define a variable for storing the area for each constellation (to be scraped from the constellation map website):
    constellations_area = {}

    # Constellation "Serpens" is represented via 2 separate entries in the target website (head & tail). Accordingly, define variable to be used
    # as part of the workaround to handle this constellation's data differently than the rest:
    serpens_element_constellation_area_text = ""

    try:
        # Initiate and configure a Selenium object to be used for scraping website for area (page 1):
        driver = setup_selenium_driver(URL_CONSTELLATION_ADD_DETAILS_2A, 1, 1)

        # Pause program execution to allow for constellation website loading time:
        time.sleep(WEB_LOADING_TIME_ALLOWANCE)

        # Define special variables to handle the 'Serpens' constellation whose data spans 2 entries (head/tail) on the target website:
        serpens_index = 0
        serpens_list = ["Head: ", "Tail: "]

        # Scrape the constellation map website to obtain additional details for each constellation:
        for i in range(1,51):  # Added 1 because the constellation "Serpens" is rep'd by two separate entries on this website

            # Find the element pertaining to the constellation's name. Decode it to normalize to ASCII-based characters:
            element_constellation_name = find_element(driver, "xpath", '/html/body/div/div[3]/div[1]/div[1]/div/div[4]/div[2]/table/tbody/tr[' + str(i) + ']/td[1]/a')
            element_constellation_name_unidecoded = unidecode.unidecode(element_constellation_name.get_attribute("text"))

            # Find the element pertaining to the constellation's area. Decode it to normalize to ASCII-based characters:
            element_constellation_area = find_element(driver, "xpath", '/html/body/div/div[3]/div[1]/div[1]/div/div[4]/div[2]/table/tbody/tr[' + str(i) + ']/td[2]')
            element_constellation_area_text = unidecode.unidecode(element_constellation_area.get_attribute("innerHTML")).replace("&nbsp;"," ")

            # Add the area collected above to the "constellation area" dictionary:
            if "Serpens" in element_constellation_name_unidecoded:  # Constellation "Serpens" is represented via 2 separate entries in the target website (head & tail).
                serpens_element_constellation_area_text += serpens_list[serpens_index] + element_constellation_area_text + " "

                constellations_area["Serpens"] = {
                    "area": serpens_element_constellation_area_text
                }

                serpens_index += 1

            else:
                constellations_area[element_constellation_name_unidecoded] = {
                    "area": element_constellation_area_text,
                }

        # Close and delete the Selenium driver object:
        driver.close()
        del driver

        # Initiate and configure a Selenium object to be used for scraping website for area (page 2:
        driver = setup_selenium_driver(URL_CONSTELLATION_ADD_DETAILS_2B, 1, 1)

        # Pause program execution to allow for constellation website loading time:
        time.sleep(WEB_LOADING_TIME_ALLOWANCE)

        # Scrape the constellation map website to obtain additional details for each constellation:
        for i in range(51,len(constellations) + 1 + 2):  # Added 1 because the constellation "Serpens" is rep'd by two separate entries on this website, and added another because website contains an "Unknown constellation" that should not detract from reaching the end of the "constellations_data" dictionary.

            # Find the element pertaining to the constellation's name. Decode it to normalize to ASCII-based characters:
            element_constellation_name = find_element(driver, "xpath", '/html/body/div/div[3]/div[1]/div[1]/div/div[4]/div[2]/table/tbody/tr[' + str(i- 50) + ']/td[1]/a')
            element_constellation_name_unidecoded = unidecode.unidecode(element_constellation_name.get_attribute("text"))

            # Find the element pertaining to the constellation's area. Decode it to normalize to ASCII-based characters:
            element_constellation_area = find_element(driver, "xpath", '/html/body/div/div[3]/div[1]/div[1]/div/div[4]/div[2]/table/tbody/tr[' + str(i - 50) + ']/td[2]')
            element_constellation_area_text = unidecode.unidecode(element_constellation_area.get_attribute("innerHTML")).replace("&nbsp;", " ")

            # Add the area collected above to the "constellation area" dictionary:
            if "Serpens" in element_constellation_name_unidecoded:  # Constellation "Serpens" is represented via 2 separate entries in the target website (head & tail).
                serpens_element_constellation_area_text += serpens_list[serpens_index] + element_constellation_area_text + " "

                constellations_area["Serpens"] = {
                    "area": serpens_element_constellation_area_text
                }

                serpens_index += 1

            else:
                constellations_area[element_constellation_name_unidecoded] = {
                    "area": element_constellation_area_text,
                }

        # Close and delete the Selenium driver object:
        driver.close()
        del driver

        # Sort the "constellation area" dictionary in alphabetical order by its key (the constellation's name):
        constellations_area = collections.OrderedDict(sorted(constellations_area.items()))

        # Return the populated "constellations_area" dictionary to the calling function:
        return constellations_area

    except Exception as err:  # An error has occurred.
        # Print error message:
        print(f"Error (Constellation Data - Area): {err}")

        # Return empty directory as a failed-execution indication to the calling function:
        return {}


def get_constellation_data_nicknames(constellations):
    """Function for getting (via web-scraping) the nickname for each constellation identified"""

    # Define a variable for storing the final (sorted) dictionary of data for each constellation
    # (for a better-formatted JSON without the "OrderedDict" qualifier):
    constellations_data = {}

    try:
        # Initiate and configure a Selenium object to be used for scraping the constellation map website:
        driver = setup_selenium_driver(URL_CONSTELLATION_MAP_SITE, 1, 1)

        # Pause program execution to allow for constellation website loading time:
        time.sleep(WEB_LOADING_TIME_ALLOWANCE)

        # Define a variable for storing the nicknames of each constellation (to be scraped from the constellation map website):
        constellation_nicknames = {}

        # Scrape the constellation map website to obtain the nicknames of each constellation:
        for i in range(1, len(constellations) + 1):
            try:
                # Find the element pertaining to the constellation's name:
                element_constellation_name = find_element(driver, "xpath", '/html/body/div[3]/section[2]/div/div/div/div[1]/div[' + str(i) + ']/div/article/div[2]/header/h2/a')

            except:  # Some of the constellations may use a different path than tbe above.
                # Find the element pertaining to the constellation's name:
                element_constellation_name = find_element(driver, "xpath", '/html/body/div[3]/section[2]/div/div/div/div[1]/div[' + str(i) + ']/div/article/div[2]/header/h3/a')

            # From the scraping performed above, decode the constellation's name to normalize to ASCII-based characters:
            element_constellation_name_unidecoded = unidecode.unidecode(element_constellation_name.text)

            # Find the element pertaining to the constellation's nickname. Decode it to normalize to ASCII-based characters:
            element_constellation_nickname = find_element(driver, "xpath", '/html/body/div[3]/section[2]/div/div/div/div[1]/div[' + str(i) + ']/div/article/div[2]/div/p')
            element_constellation_nickname_unidecoded = unidecode.unidecode(element_constellation_nickname.text)

            # Add the nickname to the "constellation nicknames" dictionary:
            constellation_nicknames[element_constellation_name_unidecoded] = element_constellation_nickname_unidecoded

        # Sort the "constellation nicknames" dictionary in alphabetical order by its key (the constellation's name):
        constellation_nicknames = collections.OrderedDict(sorted(constellation_nicknames.items()))

        # Close and delete the Selenium driver object:
        driver.close()
        del driver

        # Define a variable for storing the (unsorted) dictionary of data for each constellation:
        constellations_unsorted = {}

        # For each constellation identified, prepare its dictionary entry:
        for key in constellations:
            constellations_unsorted[constellations[key]] = {"abbreviation": key,
                                                            "nickname": constellation_nicknames[constellations[key]],
                                                            "url": "https://www.go-astronomy.com/constellations.php?Name=" +
                                                                   constellations[key].replace(" ", "%20")}

        # Sort the (unsorted) dictionary  in alphabetical order by its key (the constellation's name):
        constellations_sorted = collections.OrderedDict(sorted(constellations_unsorted.items()))

        # For each constellation identified, prepare its dictionary entry:
        for key in constellations_sorted:
            constellations_data[key] = {"abbreviation": constellations_sorted[key]["abbreviation"],
                                        "nickname": constellations_sorted[key]["nickname"],
                                        "url": constellations_sorted[key]["url"]}

        # Return the populated "constellations_data" dictionary to the calling function:
        return constellations_data

    except Exception as err:  # An error has occurred.
        # Print error message:
        print(f"Error (Constellation Data - Nicknames): {err}")

        # Return empty dictionary as a failed-execution indication to the calling function:
        return {}


def get_approaching_asteroids():
    """Function that retrieves a list of asteroids based on closest approach to Earth"""
    # Initialize variables to return info. to calling function:
    return_has_json = False

    current_date = datetime.now()
    current_date_plus_30 = current_date + timedelta(days=7)

    try:
        # Execute the API request (limit: closest approach <= 7 days from today):
        response = requests.get(URL_CLOSEST_APPROACH_ASTEROIDS + "?start_date=" + current_date.strftime("%Y-%m-%d") + "&end_date=" + current_date_plus_30.strftime("%Y-%m-%d") + "&api_key=" + API_KEY_CLOSEST_APPROACH_ASTEROIDS)

        # Initialize variable to store collected necessary asteroid data:
        approaching_asteroids = []

        # If the API request was successful, display the results:
        if response.status_code == 200:  # API request was successful.

            # Capture desired fields from the returned JSON:
            for key in response.json()["near_earth_objects"]:
                for asteroid in response.json()["near_earth_objects"][key]:
                    asteroid_dict = {
                        "id": asteroid["id"],
                        "name": asteroid["name"],
                        "absolute_magnitude_h": asteroid["absolute_magnitude_h"],
                        "estimated_diameter_km_min": asteroid["estimated_diameter"]["kilometers"]["estimated_diameter_min"],
                        "estimated_diameter_km_max": asteroid["estimated_diameter"]["kilometers"]["estimated_diameter_max"],
                        "is_potentially_hazardous": asteroid["is_potentially_hazardous_asteroid"],
                        "close_approach_date": asteroid["close_approach_data"][0]["close_approach_date"],
                        "relative_velocity_km_per_s": asteroid["close_approach_data"][0]["relative_velocity"]["kilometers_per_second"],
                        "miss_distance_km": asteroid["close_approach_data"][0]["miss_distance"]["kilometers"],
                        "orbiting_body": asteroid["close_approach_data"][0]["orbiting_body"],
                        "is_sentry_object": asteroid["is_sentry_object"],
                        "url": asteroid["nasa_jpl_url"]
                        }

                    # Add captured data for each asteroid (as a dictionary) to the "approaching_asteroids" list:
                    approaching_asteroids.append(asteroid_dict)

            # Delete the existing records in the "approaching_asteroids" database table:
            if not update_database("update_asteroids_delete_existing", {}):
                exit()

            # Import the up-to-date data (from the "approaching_asteroids" list) into the "asteroids" database table.
            if not update_database("update_asteroids_import_new", approaching_asteroids):
                exit()

            # Retrieve all existing records in the "approaching_asteroids" database table. If the function
            # called returns an empty directory, end this procedure:
            asteroids_data = retrieve_from_database("approaching_asteroids")
            if asteroids_data == {}:
                exit()

            # Create and format a spreadsheet file (workbook) to contain all asteroids data. If the function called returns an empty directory, end this procedure:
            if not export_approaching_asteroids_data_to_spreadsheet(asteroids_data):
                exit()

            # Return the populated "asteroids" list:
            return asteroids_data, True

        else:  # API request failed.
            return "Error: API request failed. Data cannot be obtained at this time.", False

    except Exception as err:  # An error has occurred.
        return "An error has occurred. Data cannot be obtained at this time.", False


def get_astronomy_pic_of_the_day():
    """Function to retrieve the astronomy picture of the day"""
    # Initialize variables to be used for returning values to the calling function:
    json = {}
    copyright_details = ""
    error_message = ""

    try:
        # Execute API request:
        url = URL_ASTRONOMY_PIC_OF_THE_DAY + "?api_key=" + API_KEY_ASTRONOMY_PIC_OF_THE_DAY
        response = requests.get(url)

        # If the API request was successful, display the results:
        if response.status_code == 200:  # API request was successful.
            # print(
            #     f"Astronomy pic of the day:\nTitle: {response.json()["title"]}\nExplanation: {response.json()["explanation"]}\nURL (HD): {response.json()["hdurl"]}\nURL (SD): {response.json()["url"]}\nMedia type: {response.json()["media_type"]}\nService version: {response.json()["service_version"]}")
            json = response.json()

            # If there is copyright info. included in the JSON, display it:
            try:
                # print(f"Copyright: {response.json()["copyright"].replace("\n", "")}")
                copyright_details = f"Copyright: {response.json()["copyright"].replace("\n", "")}"
            except:
                pass
        else:  # API request failed.
            # Print error message:
            # print("Error (Astronomy pic): API request failed. Data cannot be obtained at this time.")
            error_message = "API request failed. Data cannot be obtained at this time."

    except Exception as err:  # An error has occurred.
        # Print error message:
        # print(f"Error (Astronomy pic of the day): {err}")
        error_message = "An error has occurred. Data cannot be obtained at this time."

    # Return results to calling function:
    return json, copyright_details, error_message


def get_iss_location():
    """Function to get the current location of the ISS and a link to view the map of same"""
    # Initialize variables to be used for returning values to the calling function:
    location_address = ""
    location_url = ""

    try:
        # Execute API request:
        response = requests.get(URL_ISS_LOCATION)

        # If the API request was successful, display the results:
        if response.status_code == 200:
            latitude = response.json()["iss_position"]["latitude"]
            longitude = response.json()["iss_position"]["longitude"]

            # Execute API request (using the retrieved latitude and longitude, to
            # get a link to a map of the ISS's current location:
            url = URL_GET_LOC_FROM_LAT_AND_LON + "?lat=" + str(latitude) + "&lon=" + str(
                longitude) + "&api_key=" + API_KEY_GET_LOC_FROM_LAT_AND_LON
            response = requests.get(url)

            # If the API request was successful, display the results:
            if response.status_code == 200:  # API request was successful.
                for key in response.json():
                    if key == "error":  # Resulting JSON has an error key (possibly due to current location being over water).
                        if response.json()["error"] == "Unable to geocode":  # ISS may currently be over water.
                            location_address = "No terrestrial address is available.  ISS could be over water at the current time."

                    else:  # Terrestrial address is available.
                        # Display terrestrial address:
                        location_address = response.json()["display_name"]

                    # Break from the 'for' loop:
                    break

                # Prepare and display a link that points to the ISS's current location:
                location_url = "https://maps.google.com/?q=" + str(latitude) + "," + str(longitude)
                # location_url = "https://maps.google.com/maps?q=" + str(latitude) + "," + str(longitude)
                # print(f"ISS Location (map): {url_map} (On the map, zoom out to get a better view.)")

        else:  # API request failed.
            # Print error message:
            location_address = "API request failed. Data cannot be obtained at this time."
            location_url = ""

    except Exception as err:  # An error has occurred.
        location_address = "An error has occurred. Data cannot be obtained at this time."
        location_url = ""

    # Return location address and URL to the calling function:
    return location_address, location_url


def get_people_in_space_now():
    """Function that retrieves a list of people currently in space at the present moment"""
    # Initialize variables to return info. to calling function:
    return_has_json = False

    try:
        # Execute the API request:
        response = requests.get(URL_PEOPLE_IN_SPACE_NOW)

        # If the API request was successful, display the results:
        if response.status_code == 200:  # API request was successful.
            # Sort the resulting JSON by person's name:
            people_in_space_now = collections.OrderedDict(response.json().items())

            # Iterate through the sorted JSON and display the results:
            # for item in people_in_space_now["people"]:
            #     print (f"Person's name: {item["name"]}; Craft: {item["craft"]}")
            return people_in_space_now["people"], True

        else:  # API request failed.
            # print("Error (People in space now): API request failed. Data cannot be obtained at this time.")
            return "Error: API request failed. Data cannot be obtained at this time.", False

    except Exception as err:  # An error has occurred.
        # Print error message:
        # print(f"Error (People in space now): {err}")
        return "An error has occurred. Data cannot be obtained at this time.", False


def prepare_spreadsheet_main_contents(workbook, worksheet, name, **kwargs):
    """Function for adding and formatting spreadsheet content based on the type of content being worked on"""
    if name == "approaching_asteroids_data":
        # Capture optional arguments:
        list_name = kwargs.get("list_name", None)

        # Add/format main contents:
        i = 3
        for item in list_name:
            worksheet.write(i, 0, item.close_approach_date, prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 1, item.name, prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 2, str(item.id), prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 3, "{:.2f}".format(round(item.absolute_magnitude_h,2)), prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 4, "{:.2f}".format(round(item.estimated_diameter_km_min,2)), prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 5, "{:.2f}".format(round(item.estimated_diameter_km_max,2)), prepare_spreadsheet_get_format(workbook, "data"))
            if item.is_potentially_hazardous == 0:
                worksheet.write(i, 6, "No", prepare_spreadsheet_get_format(workbook, "data"))
            elif item.is_potentially_hazardous == 1:
                worksheet.write(i, 6, "Yes", prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 7, "{:.2f}".format(round(item.relative_velocity_km_per_s,2)), prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 8, "{:.2f}".format(round(item.miss_distance_km,2)), prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 9, item.orbiting_body, prepare_spreadsheet_get_format(workbook, "data"))
            if item.is_sentry_object == 0:
                worksheet.write(i, 10, "No", prepare_spreadsheet_get_format(workbook, "data"))
            elif item.is_sentry_object == 1:
                worksheet.write(i, 10, "Yes", prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write_url(i, 11, item.url, prepare_spreadsheet_get_format(workbook, "url"), tip="Click here for details.")
            i += 1

    elif name == "approaching_asteroids_headers":
        worksheet.write(2, 0, "Close Approach Date", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 1, "Name", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 2, "ID", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 3, "[H] Absolute Magnitude", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 4, "Estimated Diameter (km) - Min.", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 5, "Estimated Diameter (km) - Max.", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 6, "Is Potentially Hazardous?", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 7, "Relative Velocity (km/s)", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 8, "Miss Distance (km)", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 9, "Orbiting Body", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 10, "Is Sentry Object?", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 11, "URL for Details", prepare_spreadsheet_get_format(workbook, "column_headers"))

    elif name == "confirmed_planets_data":
        # Capture optional arguments:
        list_name = kwargs.get("list_name", None)

        # Add/format main contents:
        i = 3
        for item in list_name:
            worksheet.write(i, 0, item.host_name, prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 1, str(item.host_num_stars), prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 2, str(item.host_num_planets), prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 3, item.planet_name, prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 4, str(item.discovery_year), prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 5, item.discovery_method, prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 6, item.discovery_facility, prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 7, item.discovery_telescope, prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write_url(i, 8, item.url, prepare_spreadsheet_get_format(workbook, "url"), tip="Click here for details.")
            i += 1

    elif name == "confirmed_planets_headers":
        worksheet.write(2, 0, "Host Name", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 1, "# Stars", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 2, "# Planets", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 3, "Planet Name", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 4, "Discovery Year", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 5, "Discovery Method", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 6, "Discovery Facility", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 7, "Discovery Telescope", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 8, "URL for Details", prepare_spreadsheet_get_format(workbook, "column_headers"))

    elif name == "constellation_headers":
        worksheet.write(2, 0, "Name", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 1, "Abbv.", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 2, "Nickname", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 3, "URL for Details", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 4, "Area", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 5, "Mythological Association", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 6, "First Appearance", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 7, "Brightest Star", prepare_spreadsheet_get_format(workbook, "column_headers"))

    elif name == "constellation_data":
        # Capture optional arguments:
        dict_name = kwargs.get("dict_name", None)
        key = kwargs.get("key", None)
        i = kwargs.get("i", None)

        # Add/format main contents:
        worksheet.write(i, 0, key, prepare_spreadsheet_get_format(workbook, "data"))
        worksheet.write(i, 1, dict_name[key]["abbreviation"], prepare_spreadsheet_get_format(workbook, "data"))
        worksheet.write(i, 2, dict_name[key]["nickname"], prepare_spreadsheet_get_format(workbook, "data"))
        worksheet.write_url(i, 3, dict_name[key]["url"])
        worksheet.write(i, 4, dict_name[key]["area"], prepare_spreadsheet_get_format(workbook, "data"))
        worksheet.write(i, 5, dict_name[key]["myth_assoc"], prepare_spreadsheet_get_format(workbook, "data"))
        worksheet.write(i, 6, dict_name[key]["first_appear"], prepare_spreadsheet_get_format(workbook, "data"))
        if key == "Serpens":
            worksheet.write(i, 7,f"{dict_name[key]["brightest_star_name"]}\n{dict_name[key]["brightest_star_url"]}",prepare_spreadsheet_get_format(workbook, "data"))

        else:
            worksheet.write_url(i, 7, dict_name[key]["brightest_star_url"], string=f"{dict_name[key]["brightest_star_name"]}")

    elif name == "photo_details_headers":
        worksheet.write(2, 0, "Rover Name", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 1, "Earth Date", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 2, "SOL", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 3, "Pic ID", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 4, "Camera Name", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 5, "Camera Full Name", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 6, "URL", prepare_spreadsheet_get_format(workbook, "column_headers"))

    elif name == "photo_details_data":
        # Capture optional arguments:
        list_name = kwargs.get("list_name", None)
        worksheet_details = kwargs.get("worksheet_details", None)

        # Add/format main contents:
        i = 3
        print(f"Mars photos: Exporting results to spreadsheet file 'Mars Photos - Details - {worksheet_details[0]}.xlsx': Processing...")
        for j in range(worksheet_details[4], worksheet_details[5]):
            worksheet.write(i, 0, list_name[j].rover_name, prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 1, list_name[j].earth_date, prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 2, str(list_name[j].sol), prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 3, str(list_name[j].pic_id), prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 4, list_name[j].camera_name, prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 5, list_name[j].camera_full_name, prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write_url(i, 6, list_name[j].url, prepare_spreadsheet_get_format(workbook, "url"), tip="Click here for photo.")
            i += 1
        print(f"Mars photos: Exporting results to spreadsheet file 'Mars Photos - Details - {worksheet_details[0]}.xlsx': Completed.")

    elif name == "photos_available_headers":
        worksheet.write(2, 0, "Rover Name", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 1, "Earth Date", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 2, "SOL", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 3, "Cameras", prepare_spreadsheet_get_format(workbook, "column_headers"))
        worksheet.write(2, 4, "Total Photos Available", prepare_spreadsheet_get_format(workbook, "column_headers"))

    elif name == "photos_available_data":
        print(f"Mars photos: Exporting results to spreadsheet file 'Mars Photos - Summary.xlsx': Processing...")
        # Capture optional arguments:
        list_name = kwargs.get("list_name", None)

        # Add/format main contents:
        i = 3
        for item in list_name:
            worksheet.write(i, 0, item.rover_name, prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 1, item.earth_date, prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 2, str(item.sol), prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 3, item.cameras, prepare_spreadsheet_get_format(workbook, "data"))
            worksheet.write(i, 4, item.total_photos, prepare_spreadsheet_get_format(workbook, "data"))
            i += 1

        print(f"Mars photos: Exporting results to spreadsheet file 'Mars Photos - Summary.xlsx': Completed.")


def prepare_spreadsheet_supplemental_formatting(workbook, worksheet, name, current_date_time, dict_name, num_columns_minus_one, column_widths, **kwargs):
    # Add an auto-filter:
    worksheet.autofilter(2, 0, len(dict_name) + 2, num_columns_minus_one)

    # Auto-fit the worksheet:
    worksheet.autofit()

    # Set column widths as needed:
    for i in range(0, len(column_widths)):
        worksheet.set_column(i, i, column_widths[i])

    # Add and format the spreadsheet header row, and implement the following: footer, page orientation, and margins:
    if name == "approaching_asteroids":
        # Add and format the spreadsheet header row:
        worksheet.merge_range("A1:L1",f"APPROACHING ASTEROIDS DATA (as of {current_date_time}) ({'{:,}'.format(len(dict_name))} Asteroids)", prepare_spreadsheet_get_format(workbook, "spreadsheet_header"))

        # Set the footer:
        worksheet.set_footer(f"Data is from the NASA JPL Asteroid team (http://neo.jpl.nasa.gov/); API maintained by SpaceRocks Team: David Greenfield, Arezu Sarvestani, Jason English and Peter Baunach\n\n&CFile Name: &F\n&CPage &P of &N")

        # Set page orientation:
        worksheet.set_landscape()

        # Set the margins:
        worksheet.set_margins(0.5, 0.5, 1, 1)  # Left, right, top, bottom

    if name == "confirmed_planets":
        # Add and format the spreadsheet header row:
        worksheet.merge_range("A1:I1",f"CONFIRMED PLANETS DATA (as of {current_date_time}) ({'{:,}'.format(len(dict_name))} Confirmed Planets)", prepare_spreadsheet_get_format(workbook, "spreadsheet_header"))

        # Set the footer:
        worksheet.set_footer(f"This research has made use of the NASA Exoplanet Archive. Reference: DOI #10.26133/NEA12\n\n&CFile Name: &F\n&CPage &P of &N")

        # Set page orientation:
        worksheet.set_landscape()

        # Set the margins:
        worksheet.set_margins(0.5, 0.5, 1, 1)  # Left, right, top, bottom

    elif name == "constellations":
        # Add and format the spreadsheet header row:
        worksheet.merge_range("A1:H1",f"CONSTELLATION DATA (as of {current_date_time}) ({'{:,}'.format(len(dict_name))} Constellations)", prepare_spreadsheet_get_format(workbook, "spreadsheet_header"))

        # Set the footer:
        worksheet.set_footer(f"Data courtesy of: 1) Skyfield, 2) © Dominic Ford 2011–2024.; Maps: GO ASTRONOMY © 2024\n\n&CFile Name: &F\n&CPage &P of &N")

        # Set page orientation:
        worksheet.set_landscape()

        # Set the margins:
        worksheet.set_margins(0.5, 0.5, 1, 1)  # Left, right, top, bottom

    elif name == "photo_details":
        # Capture optional arguments:
        rover_name = kwargs.get("rover_name", None)
        earth_year = kwargs.get("earth_year", None)
        rover_earth_year_combo = kwargs.get("rover_earth_year_combo", None)
        rover_number_of_sheets_needed = kwargs.get("rover_number_of_sheets_needed", None)

        # Determine if rover/earth year combo needs multiple sheets:
        part_number = str(rover_earth_year_combo).split("_Part")
        if len(part_number) == 1:
            part_number = ""
        else:
            part_number = f", Part {part_number[len(part_number)-1]} of {rover_number_of_sheets_needed}"

        # Add and format the spreadsheet header row:
        worksheet.merge_range("A1:G1",f"PHOTOS TAKEN BY MARS ROVER '{str(rover_name).upper()}' - Year {str(earth_year)}{part_number} (as of {current_date_time})", prepare_spreadsheet_get_format(workbook, "spreadsheet_header"))

        # Set the footer:
        worksheet.set_footer(f"Data courtesy of https://github.com/chrisccerami/mars-photo-api, https://api.nasa.gov, and https://mars-photos.herokuapp.com/\n\n&CFile Name: &F\n&CPage &P of &N")

        # Set page orientation:
        worksheet.set_landscape()

        # Set the margins:
        worksheet.set_margins(1, 0.5, 1, 1)  # Left, right, top, bottom

    elif name == "photos_available":
        # Add and format the spreadsheet header row:
        worksheet.merge_range("A1:E1",f"SUMMARY OF PHOTOS TAKEN BY MARS ROVERS (as of {current_date_time})", prepare_spreadsheet_get_format(workbook, "spreadsheet_header"))

        # Set the footer:
        worksheet.set_footer(f"Data courtesy of https://github.com/chrisccerami/mars-photo-api, https://api.nasa.gov, and https://mars-photos.herokuapp.com/\n\n&CFile Name: &F\n&CPage &P of &N")

        # Set page orientation:
        worksheet.set_portrait()

        # Set the margins:
        worksheet.set_margins(1, 0.5, 1, 1)  # Left, right, top, bottom

    # Freeze panes (for top row and left column):
    worksheet.freeze_panes(3, 1)

    # Identify the rows to print at top of each page:
    worksheet.repeat_rows(0, 2)  # First row, last row

    # Scale the pages to fit within the page boundaries:
    worksheet.fit_to_pages(1, 0)


def prepare_spreadsheet_get_format(workbook, name):
    """Function for identifying the format to be used in formatting content in spreadsheet, based on the type of content involved"""
    if name == "column_headers":
        # Identify formatting applicable to the column headers:
        return workbook.add_format({"bold": 3, "underline": True, "font_name": "Calibri", "font_size": 11, 'text_wrap': True})

    elif name == "data":
        return workbook.add_format({"bold": 0, "font_name": "Calibri", "font_size": 11, 'text_wrap': True})

    elif name == "url":
        return workbook.add_format({"bold": 0, "font_color": "blue", "underline": 1, "font_name": "Calibri", "font_size": 11, 'text_wrap': True})

    elif name == "spreadsheet_header":
        return workbook.add_format({"bold": 3, "font_name": "Calibri", "font_size": 16})


def setup_selenium_driver(url, width, height):
    """Function for initiating and configuring a Selenium driver object"""

    # Keep Chrome browser open after program finishes:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)

    # Create and configure the Chrome driver (pass above options into the web driver):
    driver = webdriver.Chrome(options=chrome_options)

    # Access the desired URL.
    driver.get(url)

    # Set window position and dimensions, with the latter being large enough to display the website's elements needed:
    driver.set_window_position(0, 0)
    driver.set_window_size(width, height)

    # Return the Selenium driver object to the calling function:
    return driver


#*** BELOW = UNFINALIZED FUNCTIONS***

def get_mars_photos():
    """Function to retrieve summary and detailed data pertaining to the photos taken by each rover exploring on Mars"""
    # Inform user that database will be checked for updates:
    print("Mars photos: Checking for updates needed...")
    
    try:
        # Prepare a dictionary which summarizes photos available by rover and earth date:
        photos_available = get_mars_photos_summarize_photos_available({})
        if photos_available == {}:
            exit()

        # Obtain respective dictionaries summarizing photos available and the corresponding contents of the
        # "mars_photo_details" database table. If the function returns an empty directory for the former,
        # end this procedure:
        photos_available_summary, photo_details_summary = retrieve_from_database("mars_photo_details_compare_with_photos_available")
        if photos_available_summary == {}:
            exit()
        else:
            # Initialize a variable for capturing rover/earth date combinations for which there is a mismatch
            # between the photos available and the corresponding photo details:
            rover_earth_date_combo_mismatch_between_summaries = []

            # Compare photos available with the corresponding contents of the "mars_photo_details" database table:
            if photos_available_summary == photo_details_summary:  # Database is up to date.  No API requests are needed.
                print("Mars photos: Database is up to date. Proceeding to export results to spreadsheet files...")

            else:  # Database (specifically the "mars_photo_details" needs updating.
                print("Mars photos: Photo details table needs updating.  Update in progress...")

                # Capture a list of the rover/earth date combinations for which there is a mismatch
                # between the photos available and the corresponding photo details:
                for i in range(0, len(photos_available_summary)):
                    if not(photos_available_summary[i] in photo_details_summary):
                        rover_earth_date_combo_mismatch_between_summaries.append(photos_available_summary[i][0])

            # Perform required database updates based on whether any mismatches were identified above.
            # If the function called returns a failed-execution indication, end this procedure:
            if not get_mars_photos_update_database(photos_available, rover_earth_date_combo_mismatch_between_summaries):
                exit()

        # Retrieve a list of records from the "mars_photos_available" database table.  If the function
        # called returns a failed-execution indication (i.e., an empty dictionary), end this procedure:
        photos_available = retrieve_from_database("mars_photos_available")
        if photos_available == {}:
            exit()

        # Retrieve a list of records from the "mars_photo_details database table.  If the function
        # called returns a failed-execution indication (i.e., an empty dictionary), end this procedure:
        photo_details = retrieve_from_database("mars_photo_details")
        if photo_details == {}:
            exit()

        # Export collected summary and detailed results to a spreadsheet workbook:
        if not export_mars_photos_to_spreadsheet(photos_available, photo_details):
            exit()

    except Exception as err:  # An error has occurred.
        # Print error message:
        print(f"Error (Mars photos): {err}")


def get_mars_photos_summarize_photo_counts_by_rover_and_earth_year():
    """Function to summarize photo counts by rover and earth year.  This supports final spreadsheet creation"""
    try:
        with app.app_context():
            # Get counts (by rover name and year of earth date) from "mars_photo_details" database table. If the
            # function called returns a failed-execution indication (i.e., an empty dictionary), end this procedure:
            photo_counts = retrieve_from_database("mars_photo_details_get_counts_by_rover_and_earth_date")
            if photo_counts == {}:
                exit()

            # Initialize list variables needed to produce the final results to the calling function:
            photo_count_grouping_1 = []
            photo_count_grouping_2 = []

            # Add a rover name/earth year combo value to the results obtained above, and add all to a list:
            for item in photo_counts:
                photo_count_grouping_1.append([item[0], item[1], item[0]+"_"+item[1][:4], item[2]])

            # Iterate through the list created above, summarize photo counts by rover name/earth year combo, and
            # populate list with summarized data:
            # Capture the first row of data:
            rover_name_a = photo_count_grouping_1[0][0]
            earth_year_a = photo_count_grouping_1[0][1][:4]
            rover_earth_date_combo_a = photo_count_grouping_1[0][2]
            total_photos_a = photo_count_grouping_1[0][3]

            # Capture the next row of date.  Compare the rover/earth year combo with the combo from
            # the previous row.  Iterate through this process until the end of the data set has been
            # reached:
            for i in range(1,len(photo_count_grouping_1)):
                # Capture the next row of data:
                rover_name_b = photo_count_grouping_1[i][0]
                earth_year_b = photo_count_grouping_1[i][1][:4]
                rover_earth_date_combo_b = photo_count_grouping_1[i][2]
                total_photos_b = photo_count_grouping_1[i][3]

                # Compare the rover/earth year combo with the combo from the previous row:
                if rover_earth_date_combo_b != rover_earth_date_combo_a:  # New rover/earth year combo has been reached.
                    # Append the final photo count for the previous row (whose final row has been reached) to the
                    # final list to be returned to the calling function:
                    photo_count_grouping_2.append([rover_name_a, earth_year_a, rover_earth_date_combo_a, total_photos_a])
                    rover_name_a = rover_name_b
                    earth_year_a = earth_year_b
                    rover_earth_date_combo_a = rover_earth_date_combo_b
                    total_photos_a = total_photos_b
                else:  # New rover/earth year combo has NOT been reached.
                    # Continue tallying the running total for the current combo.
                    total_photos_a += total_photos_b

            # Capture the final total photo count for the final rover/earth date combo (whose final row
            # has been reached), and append it to the final list to be returned to the calling function:
            photo_count_grouping_2.append([rover_name_a, earth_year_a, rover_earth_date_combo_a, total_photos_a])

            # Return resulting list to the calling function:
            return photo_count_grouping_2

    except Exception as err:  # An error has occurred.
        # Print error message:
        print(f"Error (Mars photos - Summarize photo counts by rover and earth year): {err}")

        # Return empty dictionary as a failed-execution indication to the calling function:
        return []


def get_mars_photos_summarize_photos_available(photos_available):
    try:
        # Perform the following for each rover that is currently active:
        for rover_name in mars_rovers:
            # Execute the API request:
            url = URL_MARS_ROVER_PHOTOS_BY_ROVER + rover_name + "?api_key=" + API_KEY_MARS_ROVER_PHOTOS
            response = requests.get(url)

            # If API request was successful, capture desired data elements:
            if response.status_code == 200:  # API request was successful.
                i = 0
                for item in response.json()['photo_manifest']['photos']:
                    photos_available[rover_name + "_" + str(item["earth_date"])] = {
                        "sol": item["sol"],
                        "rover_name": rover_name,
                        "earth_date": item["earth_date"],
                        "total_photos": item['total_photos'],
                        "cameras": ','.join(item["cameras"])
                    }

                if photos_available == {}:
                    print(f"No photos are available for Mars rover {rover_name}.")
                    # return total_photos, {}
                    return {}

            else:  # API request failed.
                # Inform the user.  Rover will not be represented in the final output.
                print(f"No photos are available for Mars rover '{rover_name}'.")
                # return total_photos, {}
                return {}

        # Delete the existing records in the "mars_photos_available" database table and update same with the
        # contents of the "photos_available" dictionary.  If the function called returns a failed-execution
        # indication, end this procedure:
        if not update_database("update_mars_photos_available", photos_available):
            exit()

        # return total_photos, photos_available
        return photos_available

    except Exception as err:  # An error has occurred.
        # Print error message:
        print(f"Error (Mars rovers - Summarize photos available): {err}")
        # return -1, {}
        return {}


def get_mars_photos_update_database(photos_available, rover_earth_date_combo_mismatch_between_summaries):
    try:
        if len(rover_earth_date_combo_mismatch_between_summaries) > 0:
            # From the "photos_available" dictionary, capture a list of all unique rover name / SOL combinations represented in the dictionary:
            for i in range(0, len(rover_earth_date_combo_mismatch_between_summaries)):
                print(f"{i + 1} of {len(rover_earth_date_combo_mismatch_between_summaries)} rover/earth date combinations needing update ({round((i+1)/len(rover_earth_date_combo_mismatch_between_summaries) * 100, 1)} %)")
                photo_details_rover_earth_date_combo = []

                # Report how many records are in the database for the rover-earth date combo:
                existing_record_count = retrieve_from_database("mars_photo_details_rover_earth_date_combo_count",
                                                               rover_name=rover_earth_date_combo_mismatch_between_summaries[i].split("_")[0],
                                                               earth_date=rover_earth_date_combo_mismatch_between_summaries[i].split("_")[1])

                updated_record_count = \
                    photos_available[rover_earth_date_combo_mismatch_between_summaries[i]]["total_photos"]

                print(f"Rover '{rover_earth_date_combo_mismatch_between_summaries[i].split("_")[0]}', Earth Date {rover_earth_date_combo_mismatch_between_summaries[i].split("_")[1]} - Total Photos in DB: {existing_record_count}")
                print(f"Rover '{rover_earth_date_combo_mismatch_between_summaries[i].split("_")[0]}', Earth Date {rover_earth_date_combo_mismatch_between_summaries[i].split("_")[1]} - Total Photos (updated from API): {updated_record_count}")

                print("Update in progress.")

                dict_to_add = get_mars_photos_update_from_api(rover_earth_date_combo_mismatch_between_summaries[i].split("_")[0],
                                                                            rover_earth_date_combo_mismatch_between_summaries[i].split("_")[1])
                if dict_to_add != {}:
                    # Delete existing records in DB for this rover/earth date combo:
                    if not update_database("update_mars_photo_details_delete_existing", {},
                                           rover_name=rover_earth_date_combo_mismatch_between_summaries[i].split("_")[0],
                                           earth_date=rover_earth_date_combo_mismatch_between_summaries[i].split("_")[1]):
                        exit()

                    for j in range(0, len(dict_to_add)):
                        dict_to_add_sub = {
                            "rover_earth_date_combo": dict_to_add[j]["rover"]["name"] + "_" + dict_to_add[j][
                                "earth_date"],
                            "rover_name": dict_to_add[j]["rover"]["name"],
                            "sol": dict_to_add[j]["sol"],
                            "pic_id": dict_to_add[j]["id"],
                            "earth_date": dict_to_add[j]["earth_date"],
                            "camera_name": dict_to_add[j]["camera"]["name"],
                            "camera_full_name": dict_to_add[j]["camera"]["full_name"],
                            "url": dict_to_add[j]["img_src"]
                        }

                        photo_details_rover_earth_date_combo.append(dict_to_add_sub)

                    # Update the "mars_photo_details" database table with the contents of the "photo_details_rover_earth_date_combo" list.
                    # If the function called returns a failed-execution indication, end this procedure:
                    if not update_database("update_mars_photo_details", photo_details_rover_earth_date_combo):
                        exit()
                    else:
                        print("Update complete.")

        return True

    except Exception as err:  # An error has occurred.
        # Print error message:
        print(f"Error (Mars rovers - Perform update): {err}")
        return False


def get_mars_photos_update_from_api(rover_name, earth_date):
    """Function to retrieve, via an API request, photos available for a particular rover/earth date combination"""
    try:
        # Identify the URL which will be used as part of the API request:
        url = URL_MARS_ROVER_PHOTOS_BY_ROVER_AND_OTHER_CRITERIA + rover_name + "/photos/?api_key=" + API_KEY_MARS_ROVER_PHOTOS + "&earth_date=" + earth_date

        # Execute the API request.
        response = requests.get(url)
        if response.status_code == 200:  # API request was successful.
            # Calculate the total number of photos
            # total_photos = 0
            # for item in response.json()['photos']:
            #     total_photos += 1

            # Return the retrieved JSON to the calling function:
            return response.json()['photos']

        else:  # API request failed.
            # Inform the user that the photos cannot be obtained at this time:
            print(f"Error: Data for 'Mars Rover photos (Rover: '{rover_name}', Earth Date {earth_date}) cannot be obtained at this time.")

            # Return
            return {}

    except Exception as err:  # An error has occurred.
        # Print error message:
        print(f"Error (Mars rover - Update from API (Rover: '{rover_name}', Earth Date: {earth_date}): {err}")

        # Return an empty directory as a failed-execution indicator to the calling function:
        return {}


def get_space_news():
    """Function for retrieving the latest space news articles.rm"""
    # Initialize variables to return to calling function:
    success = True
    error_message = ""

    try:
        # Execute API request:
        response = requests.get(URL_SPACE_NEWS)
        if response.status_code == 200:
            # Delete the existing records in the "space_news" database table:
            if update_database("update_space_news_delete_existing", {}):
                # Import the newly acquired articles (from the JSON) into the "space_news" database table:
                if not update_database("update_space_news_import_new", response.json()['results']):
                    error_message = "Error: Space news articles cannot be obtained at this time."
                    success = False
            else:
                error_message = "Error: Space news articles cannot be obtained at this time."
                success = False

        else:
            error_message = "API request failed. Space news articles cannot be obtained at this time."
            success = False

    except Exception as err:  # An error has occurred.
        error_message = "An error has occurred. Space news articles cannot be obtained at this time."
        success = False

    # Return resulta to the calling function:
    return success, error_message


def update_database(trans_type, item_to_process, **kwargs):
    """Function to update this application's database based on the type of transaction"""
    try:
        with app.app_context():
            if trans_type == "update_asteroids_delete_existing":
                # Delete all records from the "approaching_asteroids" database table:
                db.session.execute(db.delete(ApproachingAsteroids))
                db.session.commit()

            elif trans_type == "update_asteroids_import_new":
                # Import the newly acquired 'approaching asteroids' data (from the "item_to_process" list) into the "confirmed_planets" database table:
                new_records = []
                for i in range(0, len(item_to_process)):
                    new_record = ApproachingAsteroids(
                        id=item_to_process[i]["id"],
                        name=item_to_process[i]["name"],
                        absolute_magnitude_h=item_to_process[i]["absolute_magnitude_h"],
                        estimated_diameter_km_min=item_to_process[i]["estimated_diameter_km_min"],
                        estimated_diameter_km_max=item_to_process[i]["estimated_diameter_km_max"],
                        is_potentially_hazardous=item_to_process[i]["is_potentially_hazardous"],
                        close_approach_date=item_to_process[i]["close_approach_date"],
                        relative_velocity_km_per_s=item_to_process[i]["relative_velocity_km_per_s"],
                        miss_distance_km=item_to_process[i]["miss_distance_km"],
                        orbiting_body=item_to_process[i]["orbiting_body"],
                        is_sentry_object=item_to_process[i]["is_sentry_object"],
                        url=item_to_process[i]["url"]
                    )

                    new_records.append(new_record)

                db.session.add_all(new_records)
                db.session.commit()

            elif trans_type == "update_confirmed_planets_import_new":
                # Import the newly acquired 'confirmed planets' data (from the "item_to_process" list) into the "confirmed_planets" database table:
                new_records = []
                for i in range(0, len(item_to_process)):
                    new_record = ConfirmedPlanets(
                        host_name=item_to_process[i]["hostname"],
                        host_num_stars=item_to_process[i]["sy_snum"],
                        host_num_planets=item_to_process[i]["sy_pnum"],
                        planet_name=item_to_process[i]["pl_name"],
                        discovery_year=item_to_process[i]["disc_year"],
                        discovery_method=item_to_process[i]["discoverymethod"],
                        discovery_facility=item_to_process[i]["disc_facility"],
                        discovery_telescope=item_to_process[i]["disc_telescope"],
                        url = f"https://exoplanetarchive.ipac.caltech.edu/overview/{item_to_process[i]["pl_name"].replace(" ","%20")}"
                    )

                    new_records.append(new_record)

                db.session.add_all(new_records)
                db.session.commit()

            elif trans_type == "update_confirmed_planets_delete_existing":
                # Delete all records from the "confirmed_planets" database table:
                db.session.execute(db.delete(ConfirmedPlanets))
                db.session.commit()

            if trans_type == "update_constellations":
                # Delete all existing records from the "constellations" database table:
                db.session.query(Constellations).delete()
                db.session.commit()

                # Upload, to the "constellations" database table, all contents of the "item_to_process"
                # parameter (in this case, the "constellations_data" directory from the calling function):
                new_records = []
                for key in item_to_process:
                    new_record = Constellations(
                        name=key,
                        abbreviation=item_to_process[key]["abbreviation"],
                        nickname=item_to_process[key]["nickname"],
                        url=item_to_process[key]["url"],
                        area=item_to_process[key]["area"],
                        myth_assoc=item_to_process[key]["myth_assoc"],
                        first_appear=item_to_process[key]["first_appear"],
                        brightest_star_name=item_to_process[key]["brightest_star_name"],
                        brightest_star_url=item_to_process[key]["brightest_star_url"]
                    )
                    new_records.append(new_record)

                db.session.add_all(new_records)
                db.session.commit()

            elif trans_type == "update_mars_photos_available":
                # Delete all existing records from the "mars_photos_available" database table:
                db.session.query(MarsPhotosAvailable).delete()
                db.session.commit()

                # Upload, to the "mars_photos_available" database table, all contents of the "item_to_process"
                # parameter (in this case, the "photos_available" directory from the calling function):
                new_records = []
                for key in item_to_process:
                    new_record = MarsPhotosAvailable(
                        rover_earth_date_combo=key,
                        rover_name=item_to_process[key]["rover_name"],
                        sol=int(item_to_process[key]["sol"]),
                        earth_date = item_to_process[key]["earth_date"],
                        cameras=item_to_process[key]["cameras"],
                        total_photos=item_to_process[key]["total_photos"]
                    )
                    new_records.append(new_record)

                db.session.add_all(new_records)
                db.session.commit()

            elif trans_type == "update_mars_photo_details":
                # Upload, to the "mars_photo_details" database table, all contents of the "item_to_process"
                # parameter (in this case, the "photo_details_rover_earth_date_combo" list from the calling function):
                new_records = []
                for i in range(0, len(item_to_process)):
                    new_record = MarsPhotoDetails(
                        rover_earth_date_combo=item_to_process[i]["rover_earth_date_combo"],
                        rover_name=item_to_process[i]["rover_name"],
                        sol=int(item_to_process[i]["sol"]),
                        pic_id=item_to_process[i]["pic_id"],
                        earth_date = item_to_process[i]["earth_date"],
                        camera_name=item_to_process[i]["camera_name"],
                        camera_full_name=item_to_process[i]["camera_full_name"],
                        url=item_to_process[i]["url"]
                    )

                    new_records.append(new_record)

                db.session.add_all(new_records)
                db.session.commit()

            elif trans_type == "update_mars_photo_details_delete_existing":
                # Capture optional arguments:
                rover_name = kwargs.get("rover_name", None)
                earth_date = kwargs.get("earth_date", None)

                # Delete, from the "mars_photo_details" database table, all records where the rover name and
                # earth date match what was passed to this function:
                db.session.execute(db.delete(MarsPhotoDetails).where(MarsPhotoDetails.rover_earth_date_combo == rover_name + "_" + earth_date))
                db.session.commit()

            elif trans_type == "update_space_news_import_new":
                # Import the newly acquired articles (from the "item_to_process" list) into the "space_news" database table:
                new_records = []
                for i in range(0, len(item_to_process)):
                    new_record = SpaceNews(
                        article_id=item_to_process[i]["id"],
                        title=item_to_process[i]["title"],
                        url=item_to_process[i]["url"],
                        summary=item_to_process[i]["summary"],
                        news_site=item_to_process[i]["news_site"],
                        date_time_published=datetime.strptime(item_to_process[i]["published_at"], "%Y-%m-%dT%H:%M:%SZ"),
                        date_time_updated=datetime.strptime(item_to_process[i]["updated_at"],"%Y-%m-%dT%H:%M:%S.%fZ")
                    )
                    new_records.append(new_record)

                db.session.add_all(new_records)
                db.session.commit()

            elif trans_type == "update_space_news_delete_existing":
                # Delete all records from the "space_news" database table:
                db.session.execute(db.delete(SpaceNews))
                db.session.commit()

        # Return successful-execution indication to the calling function:
        return True

    except Exception as err:  # An error has occurred.
        # Print error message:
        print(f"Error (Mars rover - Update database ({trans_type})': {err}")

        # Return failed-execution indication to the calling function:
        return False


def retrieve_from_database(trans_type, **kwargs):
    """Function to update this application's database based on the type of transaction"""
    try:
        with app.app_context():
            if trans_type == "approaching_asteroids_by_close_approach_date":
                # Capture optional arguments:
                close_approach_date = kwargs.get("close_approach_date", None)

                # Retrieve all existing records from the "approaching_asteroids" database table where the "close_approach_date" field matches the passed parameter:
                return db.session.execute(db.select(ApproachingAsteroids).where(ApproachingAsteroids.close_approach_date == close_approach_date).order_by(ApproachingAsteroids.name)).scalars().all()

            elif trans_type == "approaching_asteroids":
                # Retrieve all existing records from the "approaching_asteroids" database table:
                return db.session.execute(db.select(ApproachingAsteroids).order_by(ApproachingAsteroids.close_approach_date, ApproachingAsteroids.name)).scalars().all()

            elif trans_type == "confirmed_planets":
                # Retrieve all existing records from the "confirmed_planets" database table:
                return db.session.execute(db.select(ConfirmedPlanets).order_by(ConfirmedPlanets.host_name, ConfirmedPlanets.planet_name)).scalars().all()

            elif trans_type == "confirmed_planets_by_disc_year":
                # Capture optional arguments:
                disc_year = kwargs.get("disc_year", None)

                # Retrieve all existing records from the "confirmed_planets" database table where the "discovery_year" field matches the passed parameter:
                return db.session.execute(db.select(ConfirmedPlanets).where(ConfirmedPlanets.discovery_year == disc_year).order_by(ConfirmedPlanets.host_name, ConfirmedPlanets.planet_name)).scalars().all()

            elif trans_type == "constellations":
                # Retrieve all existing records from the "constellations" database table:
                constellations_list = db.session.execute(db.select(Constellations)).scalars().all()
                item_to_return = {}

                # Populate the "item_to_return" dictionary will all retrieved records from the DB:
                for i in range(0, len(constellations_list)):
                    item_to_return.update({
                        constellations_list[i].name: {
                            "abbreviation": constellations_list[i].abbreviation,
                            "nickname": constellations_list[i].nickname,
                            "url": constellations_list[i].url,
                            "area": constellations_list[i].area,
                            "myth_assoc": constellations_list[i].myth_assoc,
                            "first_appear": constellations_list[i].first_appear,
                            "brightest_star_name": constellations_list[i].brightest_star_name,
                            "brightest_star_url": constellations_list[i].brightest_star_url
                        }
                    })

            elif trans_type == "mars_photos_available":
                # Retrieve all existing records from the "mars_photos_available" database table:
                # photos_available_list = db.session.execute(db.select(MarsPhotosAvailable)).scalars().all()
                photos_available_list = db.session.execute(db.select(MarsPhotosAvailable).order_by(MarsPhotosAvailable.rover_name, MarsPhotosAvailable.earth_date.desc())).scalars().all()
                return photos_available_list

            elif trans_type == "mars_photo_details":
                # Retrieve all existing records from the "mars_photo_details" database table:
                # return db.session.execute(db.select(MarsPhotoDetails).order_by(MarsPhotoDetails.rover_earth_date_combo, MarsPhotoDetails.sol, MarsPhotoDetails.pic_id)).scalars().all()
                return db.session.execute(db.select(MarsPhotoDetails).order_by(MarsPhotoDetails.rover_name, MarsPhotoDetails.earth_date.desc(), MarsPhotoDetails.sol, MarsPhotoDetails.pic_id)).scalars().all()

            elif trans_type == "mars_photo_details_rover_earth_date_combo":
                # Capture optional arguments:
                rover_name = kwargs.get("rover_name", None)
                earth_date = kwargs.get("earth_date", None)

                # Retrieve all existing records from the "mars_photo_details" database table for the rover name and earth date passed to this function:
                return db.session.execute(db.select(MarsPhotoDetails).where(MarsPhotoDetails.rover_earth_date_combo == rover_name + "_" + earth_date).order_by(MarsPhotoDetails.sol, MarsPhotoDetails.pic_id)).scalars().all()

            elif trans_type == "mars_photo_details_rover_earth_date_combo_count":
                # Capture optional arguments:
                rover_name = kwargs.get("rover_name", None)
                earth_date = kwargs.get("earth_date", None)

                # Retrieve all existing records from the "mars_photo_details" database table for the rover name and earth date passed to this function:
                records = db.session.execute(db.select(MarsPhotoDetails).where(MarsPhotoDetails.rover_earth_date_combo == rover_name + "_" + earth_date)).scalars().all()
                return len(records)

            elif trans_type == "mars_photo_details_compare_with_photos_available":
                photos_available_summary = db.session.query(MarsPhotosAvailable).with_entities(MarsPhotosAvailable.rover_earth_date_combo, MarsPhotosAvailable.sol, MarsPhotosAvailable.total_photos).group_by(MarsPhotosAvailable.rover_earth_date_combo, MarsPhotosAvailable.sol).order_by(MarsPhotosAvailable.rover_earth_date_combo, MarsPhotosAvailable.sol).all()
                photo_details_summary = db.session.query(MarsPhotoDetails).with_entities(MarsPhotoDetails.rover_earth_date_combo, MarsPhotoDetails.sol,func.count(MarsPhotoDetails.pic_id).label("total_photos")).group_by(MarsPhotoDetails.rover_earth_date_combo, MarsPhotoDetails.sol).order_by(MarsPhotoDetails.rover_earth_date_combo, MarsPhotoDetails.sol).all()

                return photos_available_summary, photo_details_summary

            elif trans_type == "mars_photo_details_get_counts_by_rover_and_earth_date":
                return db.session.query(MarsPhotosAvailable).with_entities(MarsPhotosAvailable.rover_name, MarsPhotosAvailable.earth_date, MarsPhotosAvailable.total_photos).group_by(MarsPhotosAvailable.rover_name, MarsPhotosAvailable.earth_date).order_by(MarsPhotosAvailable.rover_name,MarsPhotosAvailable.earth_date.desc()).all()

            elif trans_type == "mars_rovers":
                # Retrieve all existing records from the "mars_rovers" database table where rovers are tagged as active (in terms of data production):
                item_to_return = []
                active_mars_rovers = db.session.execute(db.select(MarsRovers).where(MarsRovers.active == "Yes")).scalars().all()

                # Populate the "item_to_return" list will all retrieved records from the DB:
                for i in range(0, len(active_mars_rovers)):
                    item_to_return.append(active_mars_rovers[i].rover_name)

            elif trans_type == "space_news":
                # Retrieve all existing records from the "space_news" database table:
                return db.session.execute(db.select(SpaceNews).orderby(SpaceNews.article_id)).scalars().all()

        # Return populated "item_to_return" dictionary or list as a successful-execution indication to the calling function:
        return item_to_return

    except Exception as err:  # An error has occurred.
        # Print error message:
        print(f"Error (Retrieve from database ('{trans_type}'): {err}")

        # Return empty dictionary as a failed-execution indication to the calling function:
        return {}


def run_apis():
    global mars_rovers

    # Retrieve, from the database, a list of all rovers that are currently active for purposes of
    # data production.  If the function called returns an empty list, end this procedure:
    mars_rovers = retrieve_from_database("mars_rovers")
    if mars_rovers == {}:
        exit()

    # get_mars_photos()
    # get_constellation_data()
    # get_confirmed_planets()
    # get_approaching_asteroids()


# run_apis()

if __name__ == "__main__":
    app.run(debug=True, port=5003)