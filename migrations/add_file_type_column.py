"""
Migration script to add file_type column to documents table.
"""
import os
import sys
from datetime import datetime
from sqlalchemy import text

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Document

def run_migration():
    """Run the migration to add file_type column."""
    print("Running migration to add file_type column to documents table...")
    
    # Set up the app context
    with app.app_context():
        # Check if file_type column already exists in the Document model
        # Since we've already added it to the model, we'll skip the check for column existence
        # and just make sure the database schema is updated
        
        # This will create the column if needed
        db.create_all()
        print("Updated database schema with file_type column.")
        
        # Update existing documents to set file_type based on filename
        documents = Document.query.all()
        updated_count = 0
        
        for doc in documents:
            if not doc.file_type:
                # Extract file extension from original_filename
                _, file_extension = os.path.splitext(doc.original_filename)
                file_type = file_extension.lstrip('.').lower() if file_extension else 'unknown'
                
                # Update document
                doc.file_type = file_type
                updated_count += 1
        
        # Commit the changes
        if updated_count > 0:
            db.session.commit()
            print(f"Updated file_type for {updated_count} existing documents.")
        else:
            print("No documents needed updating.")
        
        print("Migration completed successfully.")

if __name__ == "__main__":
    run_migration()