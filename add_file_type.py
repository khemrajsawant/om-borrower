"""
Add file_type column to documents table
"""
from app import app
from models import db
from sqlalchemy import text

def add_file_type_column():
    with app.app_context():
        # Add file_type column if it doesn't exist
        db.session.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_type VARCHAR(20)"))
        db.session.commit()
        print("Added file_type column to documents table")

if __name__ == "__main__":
    add_file_type_column()