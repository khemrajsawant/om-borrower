"""
Maharashtra Lokadhikar Samiti - Borrower Management System
Web application version using Flask
"""
from flask import render_template, request, redirect, url_for, flash, send_file, jsonify, abort
from datetime import datetime
import os
import json
from werkzeug.utils import secure_filename
import io

# Import custom modules
import document_handler
import search_engine
import excel_handler
import utils
from models import db, Borrower, Document

# Register routes to the Flask application
def register_routes(app):
    # Create necessary directories
    if not os.path.exists(os.path.join('data', 'documents')):
        os.makedirs(os.path.join('data', 'documents'))
    
    # Configure upload folder for documents
    UPLOAD_FOLDER = os.path.join('data', 'documents')
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
    
    # Add a template filter for JSON serialization
    @app.template_filter('tojson')
    def tojson_filter(obj):
        return json.dumps(obj)
    
    # Add a template function for current year
    @app.template_filter('now')
    def now_filter(format_string='%Y'):
        return datetime.now().strftime(format_string)
    
    # Routes
    @app.route('/', methods=['GET', 'POST'])
    def index():
        """Home page with borrower list"""
        # Get all borrowers in descending order by serial_no
        # Note: Use desc() function for descending order and 
        # cast serial_no to integer for proper numeric sorting
        borrowers = Borrower.query.order_by(db.desc(db.cast(Borrower.serial_no, db.Integer))).all()
        borrowers_list = [b.to_dict() for b in borrowers]
        
        # Handle bulk update of letter status
        if request.method == 'POST':
            serial_nos = request.form.get('serial_nos', '').strip()
            letter_status = request.form.get('letter_status', '')
            
            if serial_nos and letter_status:
                serial_list = [s.strip() for s in serial_nos.split(',')]
                updated_count = 0
                
                # Update each borrower with matching serial number
                for borrower in borrowers:
                    if borrower.serial_no in serial_list:
                        borrower.letter_status = letter_status
                        updated_count += 1
                
                db.session.commit()
                flash(f'Updated letter status to "{letter_status}" for {updated_count} borrowers', 'success')
                return redirect(url_for('index'))
        
        # Get statistics
        stats = {
            'total_borrowers': len(borrowers),
            'letters_sent': len([b for b in borrowers if b.letter_status == 'Send']),
            'letters_returned': len([b for b in borrowers if b.letter_status == 'Returned Back']),
            'total_documents': Document.query.count()
        }
        
        return render_template('index.html', 
                              borrowers=borrowers_list,
                              stats=stats)
    
    @app.route('/borrower/add', methods=['GET', 'POST'])
    def add_borrower_route():
        """Add a new borrower"""
        if request.method == 'POST':
            # Extract borrower data from form
            borrower = Borrower(
                serial_no=request.form.get('serial_no'),
                date=request.form.get('date'),
                reference=request.form.get('reference'),
                borrower_name=request.form.get('borrower_name'),
                co_borrower_name=request.form.get('co_borrower_name'),
                address_line1=request.form.get('address_line1'),
                address_line2=request.form.get('address_line2'),
                village_city=request.form.get('village_city'),
                taluka=request.form.get('taluka'),
                district=request.form.get('district'),
                pin_code=request.form.get('pin_code'),
                mobile=request.form.get('mobile'),
                bank_name=request.form.get('bank_name'),
                loan_amount=request.form.get('loan_amount'),
                letter_status=request.form.get('letter_status'),
                notes=request.form.get('notes')
            )
            
            # Add borrower to the database
            db.session.add(borrower)
            db.session.commit()
            
            if borrower.id:
                flash(f'Borrower added successfully with Serial No: {borrower.serial_no}', 'success')
                return redirect(url_for('view_borrower', id=borrower.id))
            else:
                flash('Failed to add borrower. Please try again.', 'danger')
        
        # For GET request, show the add borrower form
        # Get next serial no
        last_borrower = Borrower.query.order_by(Borrower.id.desc()).first()
        next_serial_no = "001"  # Default value if no borrowers exist
        if last_borrower:
            try:
                last_serial = int(last_borrower.serial_no)
                next_serial_no = f"{last_serial + 1:03d}"
            except:
                pass
        
        today_date = datetime.now().strftime('%Y-%m-%d')
        
        # Get field options for dropdowns
        options = {
            'villages': [b.village_city for b in Borrower.query.with_entities(Borrower.village_city).distinct() if b.village_city],
            'talukas': [b.taluka for b in Borrower.query.with_entities(Borrower.taluka).distinct() if b.taluka],
            'districts': [b.district for b in Borrower.query.with_entities(Borrower.district).distinct() if b.district],
            'banks': [b.bank_name for b in Borrower.query.with_entities(Borrower.bank_name).distinct() if b.bank_name],
            'letter_statuses': ['Not Send', 'Send', 'Returned Back']
        }
        
        return render_template('add_borrower.html', 
                              next_serial_no=next_serial_no, 
                              today_date=today_date,
                              options=options)
    
    @app.route('/borrower/view/<int:id>')
    def view_borrower(id):
        """View borrower details"""
        borrower = Borrower.query.get(id)
        
        if not borrower:
            flash('Borrower not found', 'danger')
            return redirect(url_for('index'))
        
        return render_template('view_borrower.html', borrower=borrower.to_dict())
    
    @app.route('/borrower/edit/<int:id>', methods=['GET', 'POST'])
    def edit_borrower_route(id):
        """Edit an existing borrower"""
        borrower = Borrower.query.get(id)
        
        if not borrower:
            flash('Borrower not found', 'danger')
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            # Update borrower with form data
            borrower.serial_no = request.form.get('serial_no')
            borrower.date = request.form.get('date')
            borrower.reference = request.form.get('reference')
            borrower.borrower_name = request.form.get('borrower_name')
            borrower.co_borrower_name = request.form.get('co_borrower_name')
            borrower.address_line1 = request.form.get('address_line1')
            borrower.address_line2 = request.form.get('address_line2')
            borrower.village_city = request.form.get('village_city')
            borrower.taluka = request.form.get('taluka')
            borrower.district = request.form.get('district')
            borrower.pin_code = request.form.get('pin_code')
            borrower.mobile = request.form.get('mobile')
            borrower.bank_name = request.form.get('bank_name')
            borrower.loan_amount = request.form.get('loan_amount')
            borrower.letter_status = request.form.get('letter_status')
            borrower.notes = request.form.get('notes')
            borrower.updated_at = datetime.now()
            
            # Save to database
            db.session.commit()
            
            flash('Borrower information updated successfully', 'success')
            return redirect(url_for('view_borrower', id=id))
        
        # For GET request, show the edit form with current data
        # Get field options for dropdowns
        options = {
            'villages': [b.village_city for b in Borrower.query.with_entities(Borrower.village_city).distinct() if b.village_city],
            'talukas': [b.taluka for b in Borrower.query.with_entities(Borrower.taluka).distinct() if b.taluka],
            'districts': [b.district for b in Borrower.query.with_entities(Borrower.district).distinct() if b.district],
            'banks': [b.bank_name for b in Borrower.query.with_entities(Borrower.bank_name).distinct() if b.bank_name],
            'letter_statuses': ['Not Send', 'Send', 'Returned Back']
        }
        
        return render_template('edit_borrower.html', 
                              borrower=borrower.to_dict(),
                              options=options)
    
    @app.route('/borrower/delete/<int:id>', methods=['POST'])
    def delete_borrower_route(id):
        """Delete a borrower"""
        borrower = Borrower.query.get(id)
        
        if borrower:
            db.session.delete(borrower)
            db.session.commit()
            flash('Borrower deleted successfully', 'success')
        else:
            flash('Failed to delete borrower', 'danger')
        
        return redirect(url_for('index'))
    
    @app.route('/search')
    def search_page():
        """Display search page"""
        # Get field options for dropdowns
        options = {
            'villages': [b.village_city for b in Borrower.query.with_entities(Borrower.village_city).distinct() if b.village_city],
            'talukas': [b.taluka for b in Borrower.query.with_entities(Borrower.taluka).distinct() if b.taluka],
            'districts': [b.district for b in Borrower.query.with_entities(Borrower.district).distinct() if b.district],
            'banks': [b.bank_name for b in Borrower.query.with_entities(Borrower.bank_name).distinct() if b.bank_name],
            'letter_statuses': ['Not Send', 'Send', 'Returned Back']
        }
        return render_template('search.html', options=options)
    
    @app.route('/search/results', methods=['POST'])
    def search_results():
        """Search for borrowers"""
        search_type = request.form.get('search_type')
        results = []
        search_params = dict(request.form)
        
        if search_type == 'criteria':
            # Criteria-based search
            query = Borrower.query
            
            # Add filters based on form data
            if request.form.get('village_city'):
                query = query.filter(Borrower.village_city == request.form.get('village_city'))
            if request.form.get('taluka'):
                query = query.filter(Borrower.taluka == request.form.get('taluka'))
            if request.form.get('district'):
                query = query.filter(Borrower.district == request.form.get('district'))
            if request.form.get('bank_name'):
                query = query.filter(Borrower.bank_name == request.form.get('bank_name'))
            if request.form.get('reference'):
                query = query.filter(Borrower.reference.like(f"%{request.form.get('reference')}%"))
            if request.form.get('borrower_name'):
                query = query.filter(Borrower.borrower_name.like(f"%{request.form.get('borrower_name')}%"))
            if request.form.get('co_borrower_name'):
                query = query.filter(Borrower.co_borrower_name.like(f"%{request.form.get('co_borrower_name')}%"))
            
            # Order by serial_no in descending order and convert to dictionary
            results = [b.to_dict() for b in query.order_by(db.desc(db.cast(Borrower.serial_no, db.Integer))).all()]
        else:
            # Advanced search (text-based)
            search_text = request.form.get('search_text')
            if search_text:
                # Search across multiple fields
                query = Borrower.query.filter(
                    db.or_(
                        Borrower.serial_no.like(f"%{search_text}%"),
                        Borrower.reference.like(f"%{search_text}%"),
                        Borrower.borrower_name.like(f"%{search_text}%"),
                        Borrower.co_borrower_name.like(f"%{search_text}%"),
                        Borrower.village_city.like(f"%{search_text}%"),
                        Borrower.taluka.like(f"%{search_text}%"),
                        Borrower.district.like(f"%{search_text}%"),
                        Borrower.bank_name.like(f"%{search_text}%")
                    )
                )
                
                # Order by serial_no in descending order and convert to dictionary
                results = [b.to_dict() for b in query.order_by(db.desc(db.cast(Borrower.serial_no, db.Integer))).all()]
        
        # Get field options for dropdowns
        options = {
            'villages': [b.village_city for b in Borrower.query.with_entities(Borrower.village_city).distinct() if b.village_city],
            'talukas': [b.taluka for b in Borrower.query.with_entities(Borrower.taluka).distinct() if b.taluka],
            'districts': [b.district for b in Borrower.query.with_entities(Borrower.district).distinct() if b.district],
            'banks': [b.bank_name for b in Borrower.query.with_entities(Borrower.bank_name).distinct() if b.bank_name],
            'letter_statuses': ['Not Send', 'Send', 'Returned Back']
        }
        
        return render_template('search.html', 
                              results=results, 
                              search_params=search_params, 
                              options=options)
    
    @app.route('/documents/<int:borrower_id>')
    def documents(borrower_id):
        """Display documents for a borrower"""
        borrower = Borrower.query.get(borrower_id)
        
        if not borrower:
            flash('Borrower not found', 'danger')
            return redirect(url_for('index'))
        
        documents = [doc.to_dict() for doc in borrower.documents]
        
        return render_template('documents.html', 
                              borrower=borrower.to_dict(), 
                              documents=documents)
    
    @app.route('/document/upload/<int:borrower_id>', methods=['GET', 'POST'])
    def upload_document_route(borrower_id):
        """Upload a document for a borrower"""
        borrower = Borrower.query.get(borrower_id)
        
        if not borrower:
            flash('Borrower not found', 'danger')
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            # Check if the post request has the file part
            if 'document' not in request.files:
                flash('No file selected', 'danger')
                return redirect(request.url)
            
            file = request.files['document']
            
            # If user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No file selected', 'danger')
                return redirect(request.url)
            
            if file:
                # Generate a unique filename to prevent overwriting
                original_filename = secure_filename(file.filename)
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{original_filename}"
                description = request.form.get('description', '')
                
                # Save file to documents directory
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Create document record in database
                document = Document(
                    borrower_id=borrower_id,
                    filename=filename,
                    original_filename=original_filename,
                    description=description
                )
                
                db.session.add(document)
                db.session.commit()
                
                flash('Document uploaded successfully', 'success')
                return redirect(url_for('documents', borrower_id=borrower_id))
        
        return render_template('upload_document.html', borrower=borrower.to_dict())
    
    @app.route('/document/view/<int:doc_id>')
    def view_document_route(doc_id):
        """View a document"""
        document = Document.query.get(doc_id)
        
        if not document:
            flash('Document not found', 'danger')
            return redirect(url_for('index'))
        
        # Get document path
        doc_path = os.path.join(app.config['UPLOAD_FOLDER'], document.filename)
        
        if not os.path.exists(doc_path):
            flash('Document file not found', 'danger')
            return redirect(url_for('documents', borrower_id=document.borrower_id))
        
        # Return the file
        return send_file(doc_path, 
                        download_name=document.original_filename,
                        as_attachment=True)
    
    @app.route('/document/delete/<int:doc_id>', methods=['POST'])
    def delete_document_route(doc_id):
        """Delete a document"""
        document = Document.query.get(doc_id)
        
        if not document:
            flash('Document not found', 'danger')
            return redirect(url_for('index'))
        
        borrower_id = document.borrower_id
        
        # Delete file from filesystem
        doc_path = os.path.join(app.config['UPLOAD_FOLDER'], document.filename)
        if os.path.exists(doc_path):
            os.remove(doc_path)
        
        # Delete record from database
        db.session.delete(document)
        db.session.commit()
        
        flash('Document deleted successfully', 'success')
        return redirect(url_for('documents', borrower_id=borrower_id))
    
    @app.route('/export/all')
    def export_all():
        """Export all borrowers to Excel"""
        borrowers = [b.to_dict() for b in Borrower.query.order_by(db.desc(db.cast(Borrower.serial_no, db.Integer))).all()]
        
        if not borrowers:
            flash('No borrowers to export', 'warning')
            return redirect(url_for('index'))
        
        # Generate Excel file in memory
        output = io.BytesIO()
        excel_handler.export_to_excel(borrowers, output)
        output.seek(0)
        
        # Return the file
        return send_file(output, 
                        download_name=f'borrowers_{datetime.now().strftime("%Y%m%d")}.xlsx',
                        as_attachment=True,
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    @app.route('/export/search-results', methods=['POST'])
    def export_search_results():
        """Export search results to Excel"""
        results_json = request.form.get('results_json')
        
        if not results_json:
            flash('No results to export', 'warning')
            return redirect(url_for('search_page'))
        
        try:
            results = json.loads(results_json)
        except:
            flash('Invalid search results data', 'danger')
            return redirect(url_for('search_page'))
        
        if not results:
            flash('No results to export', 'warning')
            return redirect(url_for('search_page'))
        
        # Generate Excel file in memory
        output = io.BytesIO()
        excel_handler.export_to_excel(results, output)
        output.seek(0)
        
        # Return the file
        return send_file(output, 
                        download_name=f'search_results_{datetime.now().strftime("%Y%m%d")}.xlsx',
                        as_attachment=True,
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    @app.route('/import', methods=['GET', 'POST'])
    def import_route():
        """Import borrowers from Excel"""
        if request.method == 'POST':
            # Check if the post request has the file part
            if 'excel_file' not in request.files:
                flash('No file selected', 'danger')
                return redirect(request.url)
            
            file = request.files['excel_file']
            
            # If user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No file selected', 'danger')
                return redirect(request.url)
            
            if file and file.filename.endswith('.xlsx'):
                # Save file to temporary location
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
                file.save(temp_path)
                
                # Import from Excel
                try:
                    count = excel_handler.import_from_excel(temp_path)
                    flash(f'Successfully imported {count} borrowers', 'success')
                    return redirect(url_for('index'))
                except Exception as e:
                    flash(f'Error importing data: {str(e)}', 'danger')
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            else:
                flash('Please upload an Excel (.xlsx) file', 'danger')
        
        return render_template('import.html')
    
    @app.route('/api/options/<field>')
    def get_options(field):
        """API endpoint to get dropdown options for a field"""
        options = []
        
        if field == 'village_city':
            options = [b.village_city for b in Borrower.query.with_entities(Borrower.village_city).distinct() if b.village_city]
        elif field == 'taluka':
            options = [b.taluka for b in Borrower.query.with_entities(Borrower.taluka).distinct() if b.taluka]
        elif field == 'district':
            options = [b.district for b in Borrower.query.with_entities(Borrower.district).distinct() if b.district]
        elif field == 'bank_name':
            options = [b.bank_name for b in Borrower.query.with_entities(Borrower.bank_name).distinct() if b.bank_name]
        elif field == 'letter_status':
            options = ['Not Send', 'Send', 'Returned Back']
        
        return jsonify(options)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html', error='Page not found (404)'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', error='Internal server error (500)'), 500