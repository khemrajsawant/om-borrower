"""
Document Handler module for the Borrower Management System.
Handles document upload, retrieval, and management.
"""
from database import execute_query
import os
import shutil
from datetime import datetime
import uuid
import utils

def upload_document(borrower_id, file_path, description=""):
    """
    Upload a document for a borrower.
    
    Args:
        borrower_id (int): ID of the borrower
        file_path (str): Path to the document file
        description (str, optional): Description of the document
        
    Returns:
        int: ID of the uploaded document
    """
    try:
        # Generate a unique filename for storage
        original_filename = os.path.basename(file_path)
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Define target path
        upload_folder = os.path.join('data', 'documents')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        target_path = os.path.join(upload_folder, unique_filename)
        
        # Copy the file to the target path
        shutil.copy2(file_path, target_path)
        
        # Get file type
        file_type = file_extension.lstrip('.').lower()
        
        # Current timestamp for upload date
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Insert document record into the database
        query = """
        INSERT INTO documents (
            borrower_id, filename, original_filename, 
            file_path, upload_date, description, file_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            borrower_id,
            unique_filename,
            original_filename,
            target_path,
            now,
            description,
            file_type
        )
        
        # Execute the query
        execute_query(query, params, commit=True)
        
        # Get the ID of the newly inserted document
        result = execute_query("SELECT last_insert_rowid() as id", fetchall=True)
        return result[0]['id'] if result else None
    
    except Exception as e:
        print(f"Error uploading document: {e}")
        return None

def get_documents_for_borrower(borrower_id):
    """
    Get all documents for a borrower.
    
    Args:
        borrower_id (int): ID of the borrower
        
    Returns:
        list: List of document dictionaries
    """
    query = """
    SELECT id, borrower_id, filename, original_filename, 
           file_path, upload_date, description, file_type
    FROM documents
    WHERE borrower_id = ?
    ORDER BY upload_date DESC
    """
    
    return execute_query(query, (borrower_id,), fetchall=True)

def get_document_by_id(doc_id):
    """
    Get document information by ID.
    
    Args:
        doc_id (int): ID of the document
        
    Returns:
        dict: Document information, or None if not found
    """
    query = """
    SELECT id, borrower_id, filename, original_filename, 
           file_path, upload_date, description, file_type
    FROM documents
    WHERE id = ?
    """
    
    result = execute_query(query, (doc_id,), fetchall=True)
    return result[0] if result else None

def delete_document(doc_id):
    """
    Delete a document.
    
    Args:
        doc_id (int): ID of the document to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # First, get the document info to delete the file
        document = get_document_by_id(doc_id)
        
        if not document:
            return False
        
        # Delete the physical file
        file_path = os.path.join('data', 'documents', document['filename'])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete the document record from the database
        query = "DELETE FROM documents WHERE id = ?"
        execute_query(query, (doc_id,), commit=True)
        
        return True
    
    except Exception as e:
        print(f"Error deleting document: {e}")
        return False