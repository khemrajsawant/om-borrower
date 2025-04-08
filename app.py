"""
Maharashtra Lokadhikar Samiti - Borrower Management System
Main application file that initializes the web application.
"""
from flask import Flask
from models import db
import os

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For flash messages and session

# Configure database
database_url = os.environ.get("DATABASE_URL")
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