import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Centralized configuration manager loading settings from environment variables.
    """
    
    # Storage settings
    OUTPUT_BASE_DIR = os.getenv("OUTPUT_BASE_DIR", "datos")
    DEFAULT_FORMAT = os.getenv("DEFAULT_FORMAT", "excel")
    
    # Add other environment variables as needed here
    # API_KEY = os.getenv("API_KEY")
    # DB_USER = os.getenv("DB_USER")
    
config = Config()
