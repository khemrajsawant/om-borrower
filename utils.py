"""
Utility functions for the Borrower Management System.
"""
import re
import os
import shutil
import tempfile
from datetime import datetime

def is_valid_pin_code(pin_code):
    """
    Validate PIN code format (6 digits).
    
    Args:
        pin_code (str): PIN code to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return bool(re.match(r'^\d{6}$', pin_code))

def is_valid_mobile(mobile):
    """
    Validate mobile number format (10 digits).
    
    Args:
        mobile (str): Mobile number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return bool(re.match(r'^\d{10}$', mobile))

def is_valid_loan_amount(amount):
    """
    Validate loan amount (numeric).
    
    Args:
        amount (str): Loan amount to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        float(amount)
        return True
    except (ValueError, TypeError):
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
    
    try:
        date_formats = ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matches, return original
        return date_str
    
    except Exception:
        return datetime.now().strftime('%Y-%m-%d')

def create_backup(db_path):
    """
    Create a backup of the database.
    
    Args:
        db_path (str): Path to the database file
        
    Returns:
        str: Path to the backup file
    """
    if not os.path.exists(db_path):
        return None
    
    # Create backup directory if it doesn't exist
    backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'borrowers_{timestamp}.db')
    
    # Copy database to backup file
    shutil.copy2(db_path, backup_file)
    
    return backup_file

def sanitize_filename(filename):
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename (str): Filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    valid_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    sanitized = ''.join(c for c in filename if c in valid_chars)
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = 'file'
    
    return sanitized

def create_temp_file(content, suffix=None):
    """
    Create a temporary file with the given content.
    
    Args:
        content (bytes): File content
        suffix (str, optional): File extension
        
    Returns:
        str: Path to the temporary file
    """
    # Create temporary file
    fd, path = tempfile.mkstemp(suffix=suffix)
    
    try:
        # Write content to file
        with os.fdopen(fd, 'wb') as f:
            f.write(content)
        
        return path
    
    except Exception:
        os.unlink(path)
        raise
