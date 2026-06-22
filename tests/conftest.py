import os

# Set DATABASE_URL at module scope so it is available when app.db imports
# and creates the SQLAlchemy engine during pytest collection.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")