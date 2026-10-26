import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("FLASK_APP_SECRET")

DATABASE_URL = os.environ.get("DATABASE_URL")