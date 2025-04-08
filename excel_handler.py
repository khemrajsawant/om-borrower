"""
Excel Handler module for the Borrower Management System.
Handles importing and exporting borrower data to/from Excel files.
"""
import os
import pandas as pd
from datetime import datetime
from database import get_db_connection
from borrower_manager import add_borrower

def export_to_excel(borrowers, file_path):
    """
    Export borrowers to an Excel file.
    
    Args:
        borrowers (list): List of borrower dictionaries
        file_path (str): Path to save the Excel file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not borrowers:
        return False
    
    # Convert to DataFrame
    df = pd.DataFrame(borrowers)
    
    # Reorder columns
    columns = [
        'serial_no', 'date', 'reference', 'borrower_name', 'co_borrower_name',
        'address_line1', 'address_line2', 'village_city', 'taluka', 'district',
        'pin_code', 'mobile', 'bank_name', 'loan_amount', 'letter_status', 'notes'
    ]
    
    # Only include columns that exist in the DataFrame
    export_columns = [col for col in columns if col in df.columns]
    
    # Reorder columns
    df = df[export_columns]
    
    # Rename columns for better presentation
    column_names = {
        'serial_no': 'Serial No',
        'date': 'Date',
        'reference': 'Reference',
        'borrower_name': 'Borrower Name',
        'co_borrower_name': 'Co-Borrower Name',
        'address_line1': 'Address Line 1',
        'address_line2': 'Address Line 2',
        'village_city': 'Village/City',
        'taluka': 'Taluka',
        'district': 'District',
        'pin_code': 'PIN Code',
        'mobile': 'Mobile No',
        'bank_name': 'Bank Name',
        'loan_amount': 'Loan Amount',
        'letter_status': 'Letter Status',
        'notes': 'Notes'
    }
    df = df.rename(columns={col: column_names.get(col, col) for col in export_columns})
    
    # Write to Excel
    try:
        # Create a writer with xlsxwriter engine
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Borrowers')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Borrowers']
            for i, col in enumerate(df.columns):
                # Find the maximum length in the column
                max_len = max(
                    df[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2  # Add a little extra space
                
                # Set the column width
                worksheet.column_dimensions[chr(65 + i)].width = max_len
        
        return True
    
    except Exception as e:
        print(f"Error exporting to Excel: {str(e)}")
        return False

def import_from_excel(file_path):
    """
    Import borrowers from an Excel file.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        int: Number of borrowers imported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel file not found: {file_path}")
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Standardize column names
        column_mapping = {
            'Serial No': 'serial_no',
            'Date': 'date',
            'Reference': 'reference',
            'Borrower Name': 'borrower_name',
            'Co-Borrower Name': 'co_borrower_name',
            'Address Line 1': 'address_line1',
            'Address Line 2': 'address_line2',
            'Village/City': 'village_city',
            'Taluka': 'taluka',
            'District': 'district',
            'PIN Code': 'pin_code',
            'Mobile No': 'mobile',
            'Bank Name': 'bank_name',
            'Loan Amount': 'loan_amount',
            'Letter Status': 'letter_status',
            'Notes': 'notes'
        }
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Convert DataFrame to list of dictionaries
        borrowers = df.to_dict(orient='records')
        
        # Import borrowers
        count = 0
        conn = get_db_connection()
        
        try:
            for borrower in borrowers:
                # Clean up data
                for key, value in borrower.items():
                    if pd.isna(value):
                        borrower[key] = ''
                    elif key == 'date':
                        # Convert date to string
                        if isinstance(value, datetime):
                            borrower[key] = value.strftime('%Y-%m-%d')
                        else:
                            borrower[key] = str(value)
                
                # Add borrower
                add_borrower(borrower)
                count += 1
            
            conn.commit()
            return count
        
        finally:
            conn.close()
    
    except Exception as e:
        print(f"Error importing from Excel: {str(e)}")
        raise
