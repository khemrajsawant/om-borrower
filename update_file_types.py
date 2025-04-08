"""
Update file_type for existing documents based on their file extensions
"""
import os
from app import app
from models import db, Document

def update_file_types():
    with app.app_context():
        # Get all documents
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

if __name__ == "__main__":
    update_file_types()