"""
Document Handler module for the Borrower Management System.
Handles document upload, retrieval, and management.
"""
import os
import shutil
from datetime import datetime
from database import get_db_connection, create_document_directory

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
    # Create document directory if it doesn't exist
    doc_dir = create_document_directory()
    
    # Get file information
    filename = os.path.basename(file_path)
    _, ext = os.path.splitext(filename)
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{borrower_id}_{timestamp}{ext}"
    new_file_path = os.path.join(doc_dir, new_filename)
    
    # Copy file to document directory
    shutil.copy2(file_path, new_file_path)
    
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Insert document record
        cursor.execute("""
            INSERT INTO documents (
                borrower_id, filename, original_filename, file_path, 
                upload_date, description, file_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            borrower_id,
            new_filename,
            filename,
            new_file_path,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            description,
            ext.lstrip('.')
        ))
        
        # Commit changes
        conn.commit()
        
        # Get ID of new document
        doc_id = cursor.lastrowid
        
        return doc_id
    finally:
        conn.close()

def get_documents_for_borrower(borrower_id):
    """
    Get all documents for a borrower.
    
    Args:
        borrower_id (int): ID of the borrower
        
    Returns:
        list: List of document dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, borrower_id, filename, original_filename, 
                   upload_date, description, file_type
            FROM documents 
            WHERE borrower_id = ?
            ORDER BY upload_date DESC
        """, (borrower_id,))
        results = cursor.fetchall()
        
        return [dict(row) for row in results]
    finally:
        conn.close()

def get_document_by_id(doc_id):
    """
    Get document information by ID.
    
    Args:
        doc_id (int): ID of the document
        
    Returns:
        dict: Document information, or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, borrower_id, filename, original_filename, file_path,
                   upload_date, description, file_type
            FROM documents 
            WHERE id = ?
        """, (doc_id,))
        result = cursor.fetchone()
        
        if result:
            return dict(result)
        else:
            return None
    finally:
        conn.close()

def delete_document(doc_id):
    """
    Delete a document.
    
    Args:
        doc_id (int): ID of the document to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Get document information
    doc = get_document_by_id(doc_id)
    
    if not doc:
        return False
    
    # Delete file
    if os.path.exists(doc['file_path']):
        os.remove(doc['file_path'])
    
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Delete document record
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        
        # Commit changes
        conn.commit()
        
        return cursor.rowcount > 0
    finally:
        conn.close()
