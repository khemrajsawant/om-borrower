"""
Excel Handler module for the Borrower Management System.
Handles importing and exporting borrower data to/from Excel files.
"""
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from datetime import datetime
import os
from models import db, Borrower

def export_to_excel(borrowers, file_path_or_buffer):
    """
    Export borrowers to an Excel file.
    
    Args:
        borrowers (list): List of borrower dictionaries
        file_path_or_buffer (str or io.BytesIO): File path or buffer to save the Excel file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create a new workbook and select the active worksheet
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Borrowers Data"
        
        # Define column headers
        headers = [
            "Sr. No.", "Date", "Reference", "Borrower Name", "Co-Borrower Name",
            "Address Line 1", "Address Line 2", "Village/City", "Taluka",
            "District", "PIN Code", "Mobile", "Bank Name", "Loan Amount",
            "Letter Status", "Notes"
        ]
        
        # Write headers
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.font = openpyxl.styles.Font(bold=True)
            cell.fill = openpyxl.styles.PatternFill(start_color="FFCCCCCC", end_color="FFCCCCCC", fill_type="solid")
            cell.alignment = openpyxl.styles.Alignment(horizontal="center", vertical="center")
        
        # Write data
        for row_num, borrower in enumerate(borrowers, 2):
            ws.cell(row=row_num, column=1).value = borrower['serial_no']
            ws.cell(row=row_num, column=2).value = borrower['date']
            ws.cell(row=row_num, column=3).value = borrower['reference']
            ws.cell(row=row_num, column=4).value = borrower['borrower_name']
            ws.cell(row=row_num, column=5).value = borrower['co_borrower_name']
            ws.cell(row=row_num, column=6).value = borrower['address_line1']
            ws.cell(row=row_num, column=7).value = borrower['address_line2']
            ws.cell(row=row_num, column=8).value = borrower['village_city']
            ws.cell(row=row_num, column=9).value = borrower['taluka']
            ws.cell(row=row_num, column=10).value = borrower['district']
            ws.cell(row=row_num, column=11).value = borrower['pin_code']
            ws.cell(row=row_num, column=12).value = borrower['mobile']
            ws.cell(row=row_num, column=13).value = borrower['bank_name']
            ws.cell(row=row_num, column=14).value = borrower['loan_amount']
            ws.cell(row=row_num, column=15).value = borrower['letter_status']
            ws.cell(row=row_num, column=16).value = borrower['notes']
        
        # Adjust column widths to fit content
        for col_num, _ in enumerate(headers, 1):
            column_letter = openpyxl.utils.get_column_letter(col_num)
            ws.column_dimensions[column_letter].width = 15  # Set a default width
            
            # Adjust specific columns
            if col_num in [1, 2, 11, 12, 14, 15]:  # Serial No, Date, PIN, Mobile, Loan, Status
                ws.column_dimensions[column_letter].width = 12
            elif col_num in [4, 5, 13]:  # Names, Bank Name
                ws.column_dimensions[column_letter].width = 20
            elif col_num in [6, 7]:  # Address lines
                ws.column_dimensions[column_letter].width = 30
            elif col_num == 16:  # Notes
                ws.column_dimensions[column_letter].width = 40
        
        # Save the workbook
        if isinstance(file_path_or_buffer, str):
            wb.save(file_path_or_buffer)
        else:
            wb.save(file_path_or_buffer)
        
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
    try:
        # Load the workbook
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        
        # Skip header row and get data
        row_count = 0
        
        # Get all rows (skip header)
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row[0]:  # Skip empty rows (no serial number)
                continue
                
            # Create a new borrower from the Excel data
            borrower = Borrower(
                serial_no=str(row[0]) if row[0] else "",
                date=str(row[1]) if row[1] else datetime.now().strftime('%Y-%m-%d'),
                reference=str(row[2]) if row[2] else "",
                borrower_name=str(row[3]) if row[3] else "",
                co_borrower_name=str(row[4]) if row[4] else "",
                address_line1=str(row[5]) if row[5] else "",
                address_line2=str(row[6]) if row[6] else "",
                village_city=str(row[7]) if row[7] else "",
                taluka=str(row[8]) if row[8] else "",
                district=str(row[9]) if row[9] else "",
                pin_code=str(row[10]) if row[10] else "",
                mobile=str(row[11]) if row[11] else "",
                bank_name=str(row[12]) if row[12] else "",
                loan_amount=str(row[13]) if row[13] else "",
                letter_status=str(row[14]) if row[14] else "Not Send",
                notes=str(row[15]) if row[15] else ""
            )
            
            # Add to database
            db.session.add(borrower)
            row_count += 1
        
        # Commit all at once for better performance
        db.session.commit()
        
        return row_count
    except Exception as e:
        # Roll back any changes
        db.session.rollback()
        print(f"Error importing from Excel: {str(e)}")
        raise