"""
Search Engine module for the Borrower Management System.
Handles searching for borrowers based on various criteria.
"""
from database import execute_query

def search_borrowers(criteria):
    """
    Search borrowers based on the given criteria.
    
    Args:
        criteria (dict): Search criteria
        
    Returns:
        list: List of borrower dictionaries matching the criteria
    """
    if not criteria:
        return []
    
    # Build the query
    query = "SELECT * FROM borrowers WHERE "
    conditions = []
    params = []
    
    for field, value in criteria.items():
        if value:
            # Case-insensitive search with partial matches
            conditions.append(f"{field} LIKE ?")
            params.append(f"%{value}%")
    
    if not conditions:
        return []
    
    query += " AND ".join(conditions)
    query += " ORDER BY serial_no DESC"
    
    # Execute the search
    return execute_query(query, tuple(params), fetchall=True)

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
    
    # Fields to search in
    fields = [
        'serial_no', 'reference', 
        'borrower_name', 'co_borrower_name',
        'address_line1', 'address_line2',
        'village_city', 'taluka', 'district',
        'pin_code', 'mobile', 'bank_name',
        'loan_amount', 'notes'
    ]
    
    # Build the query
    query = "SELECT * FROM borrowers WHERE "
    conditions = []
    params = []
    
    for field in fields:
        conditions.append(f"{field} LIKE ?")
        params.append(f"%{search_text}%")
    
    query += " OR ".join(conditions)
    query += " ORDER BY serial_no DESC"
    
    # Execute the search
    return execute_query(query, tuple(params), fetchall=True)

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
    
    query = f"SELECT * FROM borrowers WHERE {field} LIKE ? ORDER BY serial_no DESC"
    return execute_query(query, (f"%{value}%",), fetchall=True)

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
    
    query = "SELECT * FROM borrowers WHERE letter_status = ? ORDER BY serial_no DESC"
    return execute_query(query, (status,), fetchall=True)

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
    
    query = "SELECT * FROM borrowers WHERE date BETWEEN ? AND ? ORDER BY date DESC"
    return execute_query(query, (start_date, end_date), fetchall=True)