"""
Maharashtra Lokadhikar Samiti - Borrower Management System
Main application file that initializes the web application.
"""
from flask import Flask
from models import db
import os
from pathlib import Path

# Try to load .env file if available (for local deployment)
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    env_path = Path('.') / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print("Loaded environment variables from .env file")
except ImportError:
    print("python-dotenv not installed, using environment variables directly")

# Create the Flask application
app = Flask(__name__)
# Use the secret key from environment variable or generate a random one
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

# Configure database - Use SQLite as fallback if no DATABASE_URL is provided
database_url = os.environ.get("DATABASE_URL", "sqlite:///data/borrower_management.db")
# Ensure the data directory exists for SQLite
if database_url.startswith("sqlite:///data/"):
    os.makedirs("data", exist_ok=True)

# Handle Heroku's postgres:// vs postgresql:// URL format
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
    
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy with the app
db.init_app(app)

# Create all database tables
with app.app_context():
    db.create_all()

# Import and register routes
from web_app import register_routes
register_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)