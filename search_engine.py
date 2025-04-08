"""
Search Engine module for the Borrower Management System.
Handles searching for borrowers based on various criteria.
"""
from database import get_db_connection

def search_borrowers(criteria):
    """
    Search borrowers based on the given criteria.
    
    Args:
        criteria (dict): Search criteria
        
    Returns:
        list: List of borrower dictionaries matching the criteria
    """
    # Build SQL query
    query = "SELECT * FROM borrowers WHERE 1=1"
    params = []
    
    # Add criteria to query
    for field, value in criteria.items():
        if value:
            if field in ['village_city', 'taluka', 'district', 'bank_name', 'reference']:
                query += f" AND {field} = ?"
                params.append(value)
            elif field in ['borrower_name', 'co_borrower_name']:
                query += f" AND {field} LIKE ?"
                params.append(f"%{value}%")
    
    # Add order by
    query += " ORDER BY serial_no DESC"
    
    # Execute query
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return [dict(row) for row in results]
    finally:
        conn.close()

def advanced_search(search_text):
    """
    Search borrowers with a single search text across multiple fields.
    
    Args:
        search_text (str): Text to search for
        
    Returns:
        list: List of borrower dictionaries matching the search
    """
    if not search_text:
        return []
    
    # Fields to search
    fields = [
        'borrower_name', 'co_borrower_name', 'address_line1', 'address_line2',
        'village_city', 'taluka', 'district', 'bank_name', 'reference'
    ]
    
    # Build SQL query
    query = "SELECT * FROM borrowers WHERE "
    query += " OR ".join([f"{field} LIKE ?" for field in fields])
    query += " ORDER BY serial_no DESC"
    
    # Create parameters
    params = [f"%{search_text}%"] * len(fields)
    
    # Execute query
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return [dict(row) for row in results]
    finally:
        conn.close()

def search_by_field(field, value):
    """
    Search borrowers by a specific field value.
    
    Args:
        field (str): Field to search
        value (str): Value to search for
        
    Returns:
        list: List of borrower dictionaries matching the criteria
    """
    if not field or not value:
        return []
    
    # Build SQL query
    query = f"SELECT * FROM borrowers WHERE {field} LIKE ? ORDER BY serial_no DESC"
    params = [f"%{value}%"]
    
    # Execute query
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return [dict(row) for row in results]
    finally:
        conn.close()

def search_by_letter_status(status):
    """
    Search borrowers by letter status.
    
    Args:
        status (str): Letter status to search for
        
    Returns:
        list: List of borrower dictionaries matching the status
    """
    if not status:
        return []
    
    # Build SQL query
    query = "SELECT * FROM borrowers WHERE letter_status = ? ORDER BY serial_no DESC"
    params = [status]
    
    # Execute query
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return [dict(row) for row in results]
    finally:
        conn.close()

def search_by_date_range(start_date, end_date):
    """
    Search borrowers by date range.
    
    Args:
        start_date (str): Start date (YYYY-MM-DD)
        end_date (str): End date (YYYY-MM-DD)
        
    Returns:
        list: List of borrower dictionaries in the date range
    """
    if not start_date or not end_date:
        return []
    
    # Build SQL query
    query = "SELECT * FROM borrowers WHERE date >= ? AND date <= ? ORDER BY serial_no DESC"
    params = [start_date, end_date]
    
    # Execute query
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return [dict(row) for row in results]
    finally:
        conn.close()
