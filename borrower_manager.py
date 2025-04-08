"""
Borrower Manager module for the Borrower Management System.
Handles CRUD operations for borrower data.
"""
from database import execute_query
from datetime import datetime

def add_borrower(borrower_data):
    """
    Add a new borrower to the database.
    
    Args:
        borrower_data (dict): Borrower information
        
    Returns:
        int: ID of the new borrower
    """
    # Make sure to convert loan_amount to a number
    if borrower_data.get('loan_amount') and borrower_data['loan_amount'].strip():
        try:
            loan_amount = float(borrower_data['loan_amount'])
            borrower_data['loan_amount'] = str(loan_amount)
        except ValueError:
            # If conversion fails, keep as is
            pass
    
    # Current timestamp for created_at and updated_at
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Insert the borrower into the database
    query = """
    INSERT INTO borrowers (
        serial_no, date, reference, 
        borrower_name, co_borrower_name, 
        address_line1, address_line2, 
        village_city, taluka, district, 
        pin_code, mobile, 
        bank_name, loan_amount, letter_status,
        notes, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        borrower_data.get('serial_no', ''),
        borrower_data.get('date', ''),
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
        borrower_data.get('loan_amount', ''),
        borrower_data.get('letter_status', 'Not Send'),
        borrower_data.get('notes', ''),
        now,
        now
    )
    
    # Execute the query and get the last insert ID
    execute_query(query, params, commit=True)
    
    # Get the ID of the newly inserted borrower
    result = execute_query("SELECT last_insert_rowid() as id", fetchall=True)
    return result[0]['id'] if result else None

def update_borrower(borrower_id, borrower_data):
    """
    Update an existing borrower in the database.
    
    Args:
        borrower_id (int): ID of the borrower to update
        borrower_data (dict): Updated borrower information
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Make sure to convert loan_amount to a number
    if borrower_data.get('loan_amount') and borrower_data['loan_amount'].strip():
        try:
            loan_amount = float(borrower_data['loan_amount'])
            borrower_data['loan_amount'] = str(loan_amount)
        except ValueError:
            # If conversion fails, keep as is
            pass
    
    # Current timestamp for updated_at
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Update the borrower in the database
    query = """
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
        notes = ?,
        updated_at = ?
    WHERE id = ?
    """
    
    params = (
        borrower_data.get('date', ''),
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
        borrower_data.get('loan_amount', ''),
        borrower_data.get('letter_status', 'Not Send'),
        borrower_data.get('notes', ''),
        now,
        borrower_id
    )
    
    try:
        # Execute the query
        execute_query(query, params, commit=True)
        return True
    except Exception as e:
        print(f"Error updating borrower: {e}")
        return False

def delete_borrower(borrower_id):
    """
    Delete a borrower from the database.
    
    Args:
        borrower_id (int): ID of the borrower to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Delete the borrower from the database
        query = "DELETE FROM borrowers WHERE id = ?"
        execute_query(query, (borrower_id,), commit=True)
        
        return True
    except Exception as e:
        print(f"Error deleting borrower: {e}")
        return False

def get_borrower_by_id(borrower_id):
    """
    Get borrower information by ID.
    
    Args:
        borrower_id (int): ID of the borrower
        
    Returns:
        dict: Borrower information, or None if not found
    """
    query = "SELECT * FROM borrowers WHERE id = ?"
    result = execute_query(query, (borrower_id,), fetchall=True)
    
    return result[0] if result else None

def get_all_borrowers():
    """
    Get all borrowers from the database.
    
    Returns:
        list: List of borrower dictionaries
    """
    query = "SELECT * FROM borrowers ORDER BY serial_no DESC"
    return execute_query(query, fetchall=True)

def get_field_options(field=None):
    """
    Get unique values for dropdown fields.
    
    Args:
        field (str, optional): Specific field to get options for
        
    Returns:
        dict: Dictionary of field options
    """
    fields = ['village_city', 'taluka', 'district', 'bank_name', 'reference']
    options = {}
    
    if field and field in fields:
        # Get options for a specific field
        query = f"SELECT DISTINCT {field} FROM borrowers WHERE {field} IS NOT NULL AND {field} != '' ORDER BY {field}"
        result = execute_query(query, fetchall=True)
        options[field] = [row[field] for row in result]
    else:
        # Get options for all fields
        for f in fields:
            query = f"SELECT DISTINCT {f} FROM borrowers WHERE {f} IS NOT NULL AND {f} != '' ORDER BY {f}"
            result = execute_query(query, fetchall=True)
            options[f] = [row[f] for row in result]
    
    return options