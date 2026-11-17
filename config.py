import os
from dotenv import load_dotenv


load_dotenv()

db_config = {
    "dbname": os.getenv("DB_NAME", "aircrafts"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

countries_to_track = [
    "Czechia",
    "Spain",
    "Germany",
    "Belgium",
    "Poland",
    "Portugal",
    "Austria",
    "Denmark",
    "Switzerland",
    "Italy"
]

nominatim_user_agent = "CourseworkAircraftTracker/1.0 (natanovo1972@gmail.com)"

opensky_user = os.getenv("opensky_user")
opensky_password = os.getenv("opensky_password")

