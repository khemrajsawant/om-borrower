"""
Database module for the Borrower Management System.
Handles SQLite database connections and initialization.
"""
import os
import sqlite3
from datetime import datetime

def get_db_path():
    """
    Get the path to the SQLite database file.
    Creates the data directory if it doesn't exist.
    """
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    # Create data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    return os.path.join(data_dir, 'borrowers.db')

def get_db_connection():
    """
    Establish a connection to the SQLite database.
    Returns a connection object.
    """
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db():
    """
    Initialize the database by creating tables if they don't exist.
    """
    # Get database schema from schema.sql
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
    
    with open(schema_path, 'r') as f:
        schema = f.read()
    
    # Connect to database and create tables
    conn = get_db_connection()
    conn.executescript(schema)
    conn.commit()
    conn.close()

def execute_query(query, params=(), fetchall=False, commit=False):
    """
    Execute a SQL query and optionally fetch results or commit changes.
    
    Args:
        query (str): SQL query to execute
        params (tuple): Parameters for the query
        fetchall (bool): Whether to fetch all results
        commit (bool): Whether to commit changes
        
    Returns:
        list or None: Query results if fetchall is True, otherwise None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params)
        
        if commit:
            conn.commit()
        
        if fetchall:
            result = cursor.fetchall()
            return [dict(row) for row in result]
        
        return None
    finally:
        conn.close()

def get_next_serial_no():
    """
    Get the next available serial number for a borrower.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT MAX(serial_no) FROM borrowers")
        result = cursor.fetchone()
        
        if result and result[0] is not None:
            return result[0] + 1
        else:
            return 1
    finally:
        conn.close()

def create_document_directory():
    """
    Create directory for storing uploaded documents.
    """
    doc_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'documents')
    
    # Create directory if it doesn't exist
    if not os.path.exists(doc_dir):
        os.makedirs(doc_dir)
    
    return doc_dir
