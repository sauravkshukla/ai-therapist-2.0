import os
from dotenv import load_dotenv
from pathlib import Path

# Get absolute path to project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Explicitly load .env from root directory
env_path = BASE_DIR / ".env"

load_dotenv(dotenv_path=env_path)

# Load variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
EMERGENCY_CONTACT = os.getenv("EMERGENCY_CONTACT")

# DEBUG (temporary)
print("Loaded Google Key:", GOOGLE_MAPS_API_KEY)
print("Loaded Groq Key:", GROQ_API_KEY)