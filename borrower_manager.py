"""
Borrower Manager module for the Borrower Management System.
Handles CRUD operations for borrower data.
"""
from datetime import datetime
from database import get_db_connection, get_next_serial_no, execute_query

def add_borrower(borrower_data):
    """
    Add a new borrower to the database.
    
    Args:
        borrower_data (dict): Borrower information
        
    Returns:
        int: ID of the new borrower
    """
    # Get next serial number
    serial_no = get_next_serial_no()
    
    # Get current date if not provided
    if not borrower_data.get('date'):
        borrower_data['date'] = datetime.now().strftime('%Y-%m-%d')
    
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Insert new borrower
        cursor.execute("""
            INSERT INTO borrowers (
                serial_no, date, reference, borrower_name, co_borrower_name,
                address_line1, address_line2, village_city, taluka, district,
                pin_code, mobile, bank_name, loan_amount, letter_status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            serial_no,
            borrower_data.get('date'),
            borrower_data.get('reference', ''),
            borrower_data.get('borrower_name', ''),
            borrower_data.get('co_borrower_name', ''),
            borrower_data.get('address_line1', ''),
            borrower_data.get('address_line2', ''),
            borrower_data.get('village_city', ''),
            borrower_data.get('taluka', ''),
            borrower_data.get('district', ''),
            borrower_data.get('pin_code', ''),
            borrower_data.get('mobile', ''),
            borrower_data.get('bank_name', ''),
            borrower_data.get('loan_amount', '0'),
            borrower_data.get('letter_status', 'Not Send'),
            borrower_data.get('notes', '')
        ))
        
        # Commit changes
        conn.commit()
        
        # Get ID of new borrower
        borrower_id = cursor.lastrowid
        
        return borrower_id
    finally:
        conn.close()

def update_borrower(borrower_id, borrower_data):
    """
    Update an existing borrower in the database.
    
    Args:
        borrower_id (int): ID of the borrower to update
        borrower_data (dict): Updated borrower information
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Update borrower
        cursor.execute("""
            UPDATE borrowers SET
                date = ?,
                reference = ?,
                borrower_name = ?,
                co_borrower_name = ?,
                address_line1 = ?,
                address_line2 = ?,
                village_city = ?,
                taluka = ?,
                district = ?,
                pin_code = ?,
                mobile = ?,
                bank_name = ?,
                loan_amount = ?,
                letter_status = ?,
                notes = ?
            WHERE id = ?
        """, (
            borrower_data.get('date'),
            borrower_data.get('reference', ''),
            borrower_data.get('borrower_name', ''),
            borrower_data.get('co_borrower_name', ''),
            borrower_data.get('address_line1', ''),
            borrower_data.get('address_line2', ''),
            borrower_data.get('village_city', ''),
            borrower_data.get('taluka', ''),
            borrower_data.get('district', ''),
            borrower_data.get('pin_code', ''),
            borrower_data.get('mobile', ''),
            borrower_data.get('bank_name', ''),
            borrower_data.get('loan_amount', '0'),
            borrower_data.get('letter_status', 'Not Send'),
            borrower_data.get('notes', ''),
            borrower_id
        ))
        
        # Commit changes
        conn.commit()
        
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_borrower(borrower_id):
    """
    Delete a borrower from the database.
    
    Args:
        borrower_id (int): ID of the borrower to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Delete documents for this borrower
        cursor.execute("DELETE FROM documents WHERE borrower_id = ?", (borrower_id,))
        
        # Delete borrower
        cursor.execute("DELETE FROM borrowers WHERE id = ?", (borrower_id,))
        
        # Commit changes
        conn.commit()
        
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_borrower_by_id(borrower_id):
    """
    Get borrower information by ID.
    
    Args:
        borrower_id (int): ID of the borrower
        
    Returns:
        dict: Borrower information, or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM borrowers WHERE id = ?", (borrower_id,))
        result = cursor.fetchone()
        
        if result:
            return dict(result)
        else:
            return None
    finally:
        conn.close()

def get_all_borrowers():
    """
    Get all borrowers from the database.
    
    Returns:
        list: List of borrower dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM borrowers ORDER BY serial_no DESC")
        results = cursor.fetchall()
        
        return [dict(row) for row in results]
    finally:
        conn.close()

def get_field_options(field=None):
    """
    Get unique values for dropdown fields.
    
    Args:
        field (str, optional): Specific field to get options for
        
    Returns:
        dict: Dictionary of field options
    """
    fields = [
        'reference', 'village_city', 'taluka', 'district', 'bank_name'
    ] if field is None else [field]
    
    options = {}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for f in fields:
            cursor.execute(f"SELECT DISTINCT {f} FROM borrowers WHERE {f} != '' ORDER BY {f}")
            results = cursor.fetchall()
            options[f] = [row[0] for row in results]
        
        return options
    finally:
        conn.close()
