"""
Utility functions for the Borrower Management System.
"""
import re
import os
import shutil
import tempfile
import mimetypes
from datetime import datetime
import sqlite3

def is_valid_pin_code(pin_code):
    """
    Validate PIN code format (6 digits).
    
    Args:
        pin_code (str): PIN code to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not pin_code:
        return True  # PIN code is optional
    
    return bool(re.match(r'^\d{6}$', pin_code))

def is_valid_mobile(mobile):
    """
    Validate mobile number format (10 digits).
    
    Args:
        mobile (str): Mobile number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not mobile:
        return True  # Mobile number is optional
    
    return bool(re.match(r'^\d{10}$', mobile))

def is_valid_loan_amount(amount):
    """
    Validate loan amount (numeric).
    
    Args:
        amount (str): Loan amount to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not amount:
        return True  # Loan amount is optional
    
    try:
        float(amount)
        return True
    except ValueError:
        return False

def format_date(date_str):
    """
    Format date string to YYYY-MM-DD.
    
    Args:
        date_str (str): Date string to format
        
    Returns:
        str: Formatted date string
    """
    if not date_str:
        return datetime.now().strftime('%Y-%m-%d')
    
    # Try to parse common date formats
    formats = ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # If no format matches, return original
    return date_str

def create_backup(db_path):
    """
    Create a backup of the database.
    
    Args:
        db_path (str): Path to the database file
        
    Returns:
        str: Path to the backup file
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")
    
    # Create backup directory if it doesn't exist
    backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"borrowers_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Create backup
    shutil.copy2(db_path, backup_path)
    
    return backup_path

def sanitize_filename(filename):
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename (str): Filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove any characters that are not alphanumeric, period, hyphen, or underscore
    filename = re.sub(r'[^\w\-\.]', '', filename)
    
    return filename

def create_temp_file(content, suffix=None):
    """
    Create a temporary file with the given content.
    
    Args:
        content (bytes): File content
        suffix (str, optional): File extension
        
    Returns:
        str: Path to the temporary file
    """
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    
    try:
        with os.fdopen(fd, 'wb') as temp_file:
            temp_file.write(content)
    except:
        os.close(fd)
        raise
    
    return temp_path

def get_file_mime_type(file_path):
    """
    Get the MIME type of a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: MIME type of the file
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'

def get_file_type_from_extension(filename):
    """
    Get the file type from the filename extension.
    
    Args:
        filename (str): Filename
        
    Returns:
        str: File type (extension without dot)
    """
    _, extension = os.path.splitext(filename)
    return extension[1:].lower() if extension else ''

def is_previewable(file_type):
    """
    Check if a file type is previewable in a browser.
    
    Args:
        file_type (str): File type (extension without dot)
        
    Returns:
        tuple: (is_previewable, preview_type)
            - is_previewable: True if previewable, False otherwise
            - preview_type: 'image', 'pdf', 'text', or None
    """
    # Ensure file_type is lowercase for comparison
    file_type = file_type.lower() if file_type else ''
    
    # Image types
    if file_type in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']:
        return True, 'image'
    
    # PDF documents
    if file_type == 'pdf':
        return True, 'pdf'
    
    # Text files
    if file_type in ['txt', 'csv', 'json', 'xml', 'md', 'html', 'htm', 'log']:
        return True, 'text'
    
    # Not previewable
    return False, None

def get_preview_mode(mime_type):
    """
    Get the preview mode based on MIME type.
    
    Args:
        mime_type (str): MIME type of the file
        
    Returns:
        str: 'image', 'pdf', 'text', or None
    """
    if not mime_type:
        return None
    
    if mime_type.startswith('image/'):
        return 'image'
    
    if mime_type == 'application/pdf':
        return 'pdf'
    
    if mime_type.startswith('text/') or mime_type in [
        'application/json', 'application/xml', 
        'application/javascript', 'application/csv'
    ]:
        return 'text'
    
    return None