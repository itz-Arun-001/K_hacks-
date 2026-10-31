"""Loads settings from the environment (.env). Never hard-code keys here."""
import os

from dotenv import load_dotenv

load_dotenv()  # reads .env if present

# SQLite locally, or the shared Neon Postgres connection string.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./surakshit.db")

# Used later by other layers; kept here so everyone reads settings in one place.
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
SAFE_BROWSING_API_KEY = os.getenv("SAFE_BROWSING_API_KEY", "")
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
