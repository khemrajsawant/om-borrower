"""
Excel Handler module for the Borrower Management System.
Handles importing and exporting borrower data to/from Excel files.
"""
import openpyxl
import database
from datetime import datetime
import os
import borrower_manager

def export_to_excel(borrowers, file_path_or_buffer):
    """
    Export borrowers to an Excel file.
    
    Args:
        borrowers (list): List of borrower dictionaries
        file_path_or_buffer (str or io.BytesIO): File path or buffer to save the Excel file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not borrowers:
        return False
    
    try:
        # Create a new Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Borrowers"
        
        # Define headers
        headers = [
            'Serial No', 'Date', 'Reference',
            'Borrower Name', 'Co-Borrower Name',
            'Address Line 1', 'Address Line 2',
            'Village/City', 'Taluka', 'District',
            'PIN Code', 'Mobile No',
            'Bank Name', 'Loan Amount', 'Letter Status',
            'Notes'
        ]
        
        # Field mapping for database to Excel
        field_mapping = {
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
        
        # Write headers
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            # Apply header style
            cell.font = openpyxl.styles.Font(bold=True)
            cell.fill = openpyxl.styles.PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
        
        # Write borrower data
        for row_num, borrower in enumerate(borrowers, 2):
            for col_num, field in enumerate(field_mapping.keys(), 1):
                cell = ws.cell(row=row_num, column=col_num)
                cell.value = borrower.get(field, '')
        
        # Auto-adjust column widths
        for col_num, _ in enumerate(headers, 1):
            column_letter = openpyxl.utils.get_column_letter(col_num)
            ws.column_dimensions[column_letter].width = 15
        
        # Save the workbook
        if isinstance(file_path_or_buffer, str):
            wb.save(file_path_or_buffer)
        else:
            wb.save(file_path_or_buffer)
        
        return True
    
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
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
        # Load the Excel workbook
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        
        # Get headers from the first row
        headers = []
        for cell in ws[1]:
            headers.append(cell.value)
        
        # Field mapping for Excel to database
        field_mapping = {
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
        
        # Create a mapping of column indices to database fields
        column_mapping = {}
        for col_idx, header in enumerate(headers):
            if header in field_mapping:
                column_mapping[col_idx] = field_mapping[header]
        
        # Get the next available serial number if needed
        next_serial_no = database.get_next_serial_no()
        
        # Process each row (skip the header row)
        imported_count = 0
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
            borrower_data = {}
            
            # Check if the row has valid data (at least borrower name)
            if not row or not any(row):
                continue
            
            # Extract data from each cell
            for col_idx, cell_value in enumerate(row):
                if col_idx in column_mapping:
                    field_name = column_mapping[col_idx]
                    borrower_data[field_name] = str(cell_value) if cell_value is not None else ''
            
            # Ensure required fields are present
            if not borrower_data.get('borrower_name'):
                print(f"Skipping row {row_idx}: Missing borrower name")
                continue
            
            # Set serial number if not provided
            if not borrower_data.get('serial_no'):
                borrower_data['serial_no'] = str(next_serial_no)
                next_serial_no += 1
            
            # Set date if not provided
            if not borrower_data.get('date'):
                borrower_data['date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Set default letter status if not provided
            if not borrower_data.get('letter_status'):
                borrower_data['letter_status'] = 'Not Send'
            
            # Validate and standardize the letter status
            letter_status = borrower_data.get('letter_status', '').strip()
            if letter_status.lower() in ['not send', 'not sent']:
                borrower_data['letter_status'] = 'Not Send'
            elif letter_status.lower() in ['send', 'sent']:
                borrower_data['letter_status'] = 'Send'
            elif letter_status.lower() in ['returned', 'returned back']:
                borrower_data['letter_status'] = 'Returned Back'
            else:
                borrower_data['letter_status'] = 'Not Send'  # Default
            
            # Add the borrower to the database
            borrower_id = borrower_manager.add_borrower(borrower_data)
            
            if borrower_id:
                imported_count += 1
        
        return imported_count
    
    except Exception as e:
        print(f"Error importing from Excel: {e}")
        raise