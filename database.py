"""
Database module for the Borrower Management System.
Handles SQLite database connections and initialization.
"""
import sqlite3
import os

def get_db_path():
    """
    Get the path to the SQLite database file.
    Creates the data directory if it doesn't exist.
    """
    data_dir = os.path.join(os.getcwd(), 'data')
    
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
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def init_db():
    """
    Initialize the database by creating tables if they don't exist.
    """
    conn = get_db_connection()
    
    # Read schema from file
    schema_path = os.path.join(os.getcwd(), 'schema.sql')
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    
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
            result = [dict(row) for row in cursor.fetchall()]
            return result
        elif cursor.description:
            # If there's a description but not fetchall, get the first row
            row = cursor.fetchone()
            return dict(row) if row else None
        
        return None
    except Exception as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        conn.close()

def get_next_serial_no():
    """
    Get the next available serial number for a borrower.
    """
    result = execute_query("SELECT MAX(serial_no) as max_serial FROM borrowers", fetchall=True)
    
    if result and result[0]['max_serial'] is not None:
        return int(result[0]['max_serial']) + 1
    else:
        return 1  # First serial number

def create_document_directory():
    """
    Create directory for storing uploaded documents.
    """
    doc_dir = os.path.join(os.getcwd(), 'data', 'documents')
    
    if not os.path.exists(doc_dir):
        os.makedirs(doc_dir)