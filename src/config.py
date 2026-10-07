import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory setup
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# API Keys & Credentials
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

# Server Settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# AI Model Configuration
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Data Directories & Storage Paths
DATA_DIR = SRC_DIR / "data"
NOTES_DIR = DATA_DIR / "notes"
USER_PROFILE_PATH = DATA_DIR / "user_profile.json"
USER_PROFILE_EXAMPLE_PATH = DATA_DIR / "user_profile.example.json"
MEMORY_DB_PATH = DATA_DIR / "memory.db"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
NOTES_DIR.mkdir(parents=True, exist_ok=True)
