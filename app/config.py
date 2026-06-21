"""Application configuration."""
import os

APP_NAME = os.getenv("APP_NAME", "event-api")
DATABASE_URL = os.getenv("DATABASE_URL")
