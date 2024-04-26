from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.
mongo_db_uri = os.getenv("MONGO_DB_URI")

