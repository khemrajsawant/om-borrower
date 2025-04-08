"""
Database models for the Borrower Management System
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

class Borrower(db.Model):
    """Model for borrower information"""
    __tablename__ = 'borrowers'
    
    id = db.Column(db.Integer, primary_key=True)
    serial_no = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(30), nullable=False)  # Increased from 10 to 30
    reference = db.Column(db.String(255))  # Increased from 100 to 255
    borrower_name = db.Column(db.String(255), nullable=False)
    co_borrower_name = db.Column(db.String(255))
    address_line1 = db.Column(db.String(255))
    address_line2 = db.Column(db.String(255))
    village_city = db.Column(db.String(255))  # Increased from 100 to 255
    taluka = db.Column(db.String(255))  # Increased from 100 to 255
    district = db.Column(db.String(255))  # Increased from 100 to 255
    pin_code = db.Column(db.String(20))  # Increased from 10 to 20
    mobile = db.Column(db.String(20))  # Increased from 15 to 20
    bank_name = db.Column(db.String(255))  # Increased from 100 to 255
    loan_amount = db.Column(db.String(30))  # Increased from 20 to 30
    letter_status = db.Column(db.String(30), default='Not Send')  # Increased from 20 to 30
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with documents
    documents = db.relationship('Document', backref='borrower', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert borrower object to dictionary"""
        return {
            'id': self.id,
            'serial_no': self.serial_no,
            'date': self.date,
            'reference': self.reference,
            'borrower_name': self.borrower_name,
            'co_borrower_name': self.co_borrower_name,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'village_city': self.village_city,
            'taluka': self.taluka,
            'district': self.district,
            'pin_code': self.pin_code,
            'mobile': self.mobile,
            'bank_name': self.bank_name,
            'loan_amount': self.loan_amount,
            'letter_status': self.letter_status,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class Document(db.Model):
    """Model for document information"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrowers.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.now)
    file_type = db.Column(db.String(20))
    
    def to_dict(self):
        """Convert document object to dictionary"""
        # Get file type safely, ensuring it never returns None
        file_type = self.file_type if self.file_type else self.get_file_type()
        
        return {
            'id': self.id,
            'borrower_id': self.borrower_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'description': self.description,
            'uploaded_at': self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if self.uploaded_at else None,
            'upload_date': self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if self.uploaded_at else None,
            'file_type': file_type
        }
        
    def get_file_type(self):
        """Get the file type from the filename extension"""
        _, extension = os.path.splitext(self.original_filename)
        return extension.lstrip('.').lower() if extension else 'unknown'
        
    def is_previewable(self):
        """Check if the document is previewable in a browser"""
        from utils import is_previewable
        
        # Get file type, ensuring it's never None
        file_type = self.file_type if self.file_type else self.get_file_type()
        
        # Default to 'unknown' if still None somehow
        if not file_type:
            file_type = 'unknown'
            
        return is_previewable(file_type)
        
    def get_preview_url(self):
        """Get the URL for previewing the document"""
        is_preview, preview_type = self.is_previewable()
        if not is_preview:
            return None
        
        # Return the URL for the document
        return f"/document/view/{self.id}"
        
    def get_preview_type(self):
        """Get the preview type for the document"""
        _, preview_type = self.is_previewable()
        return preview_type