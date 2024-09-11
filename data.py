import os
import datetime
from dotenv import load_dotenv

# Load environmental variables from the ".env" file:
load_dotenv()

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

# Define constants to be used for e-mailing messages submitted via the "Contact Us" web page:
SENDER_EMAIL_GMAIL = os.getenv("SENDER_EMAIL_GMAIL")
SENDER_PASSWORD_GMAIL = os.getenv("SENDER_PASSWORD_GMAIL") # App password (for the app "Python e-mail", NOT the normal password for the account).
SENDER_HOST = os.getenv("SENDER_HOST")
SENDER_PORT = str(os.getenv("SENDER_PORT"))

# Define constant for web page loading-time allowance (in seconds) for the web-scrapers:
WEB_LOADING_TIME_ALLOWANCE = 5

# Create a dictionary to store spreadsheet-related attributes by content type:
spreadsheet_attributes = {
    "approaching_asteroids": {
        "wrkbk_name": "ApproachingAsteroids.xlsx",
        "wksht_name": "Approaching Asteroids",
        "headers": "approaching_asteroids_headers",
        "data_to_export_name": "approaching_asteroids_data",
        "supp_fmtg": "approaching_asteroids",
        "num_cols_minus_one": 11,
        "col_widths": (12, 20, 10, 15, 15, 15, 15, 12, 12, 10, 10, 65)
        },
    "confirmed_planets": {
        "wrkbk_name": "ConfirmedPlanets.xlsx",
        "wksht_name": "Confirmed Planets",
        "headers": "confirmed_planets_headers",
        "data_to_export_name": "confirmed_planets_data",
        "supp_fmtg": "confirmed_planets",
        "num_cols_minus_one": 8,
        "col_widths": (15, 10, 10, 15, 10, 15, 30, 20, 65)
    },
    "constellations": {
        "wrkbk_name": "Constellations.xlsx",
        "wksht_name": "Constellations",
        "headers": "constellation_headers",
        "data_to_export_name": "constellation_data",
        "supp_fmtg": "constellations",
        "num_cols_minus_one": 7,
        "col_widths": (15, 7.8, 15, 75, 15, 20, 15, 53)
    }
}

# Create a dictionary to store recognition merit by content type:
recognition = {
    "approaching_asteroids":
        "Data is from the NASA JPL Asteroid team (http://neo.jpl.nasa.gov/); API maintained by SpaceRocks Team: David Greenfield, Arezu Sarvestani, Jason English and Peter Baunach",
    "astronomy_pic_of_day":
        "Data copyrighted by Laura Rowe (Used with permission); Picture manifestation courtesy of https://apod.nasa.gov",
    "confirmed_planets":
        "This research has made use of the NASA Exoplanet Archive. Reference: DOI #10.26133/NEA12",
    "constellations":
        f"Data courtesy of: 1) Skyfield, 2) © Dominic Ford 2011–{datetime.datetime.now().year}; Maps: GO ASTRONOMY © {datetime.datetime.now().year}",
    "mars_photos":
        "Data courtesy of https://github.com/chrisccerami/mars-photo-api, https://api.nasa.gov, and https://mars-photos.herokuapp.com",
    "photo_details":
        "Data courtesy of https://github.com/chrisccerami/mars-photo-api, https://api.nasa.gov, and https://mars-photos.herokuapp.com",
    "photos_available":
        "Data courtesy of https://github.com/chrisccerami/mars-photo-api, https://api.nasa.gov, and https://mars-photos.herokuapp.com",
    "space_news":
        "Data courtesy of Spaceflight News API (SNAPI), a product by The Space Devs (TSD)",
    "web_template":
        f"Website template created by the Bootstrap team · © {datetime.datetime.now().year}",
    "where_is_iss":
        f"Data courtesy of Nathan Bergey (@natronics) and © OpenStreetMap contributors, ODbL 1.0; Reverse Geocoding courtesy of Map Maker by My Maps Inc. © Copyright 2008-{datetime.datetime.now().year} All Rights Reserved; Maps: @{datetime.datetime.now().year} Google",
    "who_is_in_space_now":
        "Data courtesy of Nathan Bergey (@natronics)"
}

# Define list variable for storing names of Mars rovers that are currently active for the purpose of data production:
mars_rovers = []

# Define variable to represent the Flask application object to be used for this website:
app = None

# Define variable to represent the database supporting this website:
db = None

# Initialize class variables for database tables:
ApproachingAsteroids = None
ConfirmedPlanets = None
Constellations = None
MarsPhotoDetails = None
MarsPhotosAvailable = None
MarsRoverCameras = None
MarsRovers = None
SpaceNews = None

# Initialize class variables for web forms:
AdminUpdateForm = None
ContactForm = None
DisplayApproachingAsteroidsSheetForm = None
DisplayConfirmedPlanetsSheetForm = None
DisplayConstellationSheetForm = None
DisplayMarsPhotosSheetForm = None
ViewApproachingAsteroidsForm = None
ViewConfirmedPlanetsForm = None
ViewConstellationForm = None
ViewMarsPhotosForm = None