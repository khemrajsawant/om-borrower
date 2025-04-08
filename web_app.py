"""
Maharashtra Lokadhikar Samiti - Borrower Management System
Web application version using Flask
"""
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, abort
from datetime import datetime
import os
import json
from werkzeug.utils import secure_filename
import io

# Import custom modules
import database
import borrower_manager
import document_handler
import search_engine
import excel_handler
import utils

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For flash messages and session

# Create necessary directories
database.init_db()
database.create_document_directory()

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
@app.route('/')
def index():
    """Home page with borrower list"""
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of borrowers per page
    
    # Get all borrowers
    borrowers = borrower_manager.get_all_borrowers()
    
    # Calculate pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_borrowers = borrowers[start:end]
    
    # Get statistics
    stats = {
        'total_borrowers': len(borrowers),
        'letters_sent': len([b for b in borrowers if b['letter_status'] == 'Send']),
        'letters_returned': len([b for b in borrowers if b['letter_status'] == 'Returned Back']),
        'total_documents': sum(len(document_handler.get_documents_for_borrower(b['id'])) for b in borrowers)
    }
    
    return render_template('index.html', 
                          borrowers=paginated_borrowers, 
                          page=page, 
                          per_page=per_page, 
                          stats=stats)


@app.route('/borrower/add', methods=['GET', 'POST'])
def add_borrower_route():
    """Add a new borrower"""
    if request.method == 'POST':
        # Extract borrower data from form
        borrower_data = {
            'serial_no': request.form.get('serial_no'),
            'date': request.form.get('date'),
            'reference': request.form.get('reference'),
            'borrower_name': request.form.get('borrower_name'),
            'co_borrower_name': request.form.get('co_borrower_name'),
            'address_line1': request.form.get('address_line1'),
            'address_line2': request.form.get('address_line2'),
            'village_city': request.form.get('village_city'),
            'taluka': request.form.get('taluka'),
            'district': request.form.get('district'),
            'pin_code': request.form.get('pin_code'),
            'mobile': request.form.get('mobile'),
            'bank_name': request.form.get('bank_name'),
            'loan_amount': request.form.get('loan_amount'),
            'letter_status': request.form.get('letter_status'),
            'notes': request.form.get('notes')
        }
        
        # Add borrower to the database
        borrower_id = borrower_manager.add_borrower(borrower_data)
        
        if borrower_id:
            flash(f'Borrower added successfully with Serial No: {borrower_data["serial_no"]}', 'success')
            return redirect(url_for('view_borrower', id=borrower_id))
        else:
            flash('Failed to add borrower. Please try again.', 'danger')
    
    # For GET request, show the add borrower form
    next_serial_no = database.get_next_serial_no()
    today_date = datetime.now().strftime('%Y-%m-%d')
    options = borrower_manager.get_field_options()
    
    return render_template('add_borrower.html', 
                          next_serial_no=next_serial_no, 
                          today_date=today_date,
                          options=options)


@app.route('/borrower/view/<int:id>')
def view_borrower(id):
    """View borrower details"""
    borrower = borrower_manager.get_borrower_by_id(id)
    
    if not borrower:
        flash('Borrower not found', 'danger')
        return redirect(url_for('index'))
    
    return render_template('view_borrower.html', borrower=borrower)


@app.route('/borrower/edit/<int:id>', methods=['GET', 'POST'])
def edit_borrower_route(id):
    """Edit an existing borrower"""
    borrower = borrower_manager.get_borrower_by_id(id)
    
    if not borrower:
        flash('Borrower not found', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Extract updated borrower data from form
        borrower_data = {
            'serial_no': request.form.get('serial_no'),
            'date': request.form.get('date'),
            'reference': request.form.get('reference'),
            'borrower_name': request.form.get('borrower_name'),
            'co_borrower_name': request.form.get('co_borrower_name'),
            'address_line1': request.form.get('address_line1'),
            'address_line2': request.form.get('address_line2'),
            'village_city': request.form.get('village_city'),
            'taluka': request.form.get('taluka'),
            'district': request.form.get('district'),
            'pin_code': request.form.get('pin_code'),
            'mobile': request.form.get('mobile'),
            'bank_name': request.form.get('bank_name'),
            'loan_amount': request.form.get('loan_amount'),
            'letter_status': request.form.get('letter_status'),
            'notes': request.form.get('notes')
        }
        
        # Update borrower in the database
        success = borrower_manager.update_borrower(id, borrower_data)
        
        if success:
            flash('Borrower information updated successfully', 'success')
            return redirect(url_for('view_borrower', id=id))
        else:
            flash('Failed to update borrower information. Please try again.', 'danger')
    
    # For GET request, show the edit form with current data
    options = borrower_manager.get_field_options()
    
    return render_template('edit_borrower.html', 
                          borrower=borrower,
                          options=options)


@app.route('/borrower/delete/<int:id>', methods=['POST'])
def delete_borrower_route(id):
    """Delete a borrower"""
    # Delete all documents for this borrower first
    documents = document_handler.get_documents_for_borrower(id)
    for doc in documents:
        document_handler.delete_document(doc['id'])
    
    # Then delete the borrower
    success = borrower_manager.delete_borrower(id)
    
    if success:
        flash('Borrower deleted successfully', 'success')
    else:
        flash('Failed to delete borrower', 'danger')
    
    return redirect(url_for('index'))


@app.route('/search')
def search_page():
    """Display search page"""
    options = borrower_manager.get_field_options()
    return render_template('search.html', options=options)


@app.route('/search/results', methods=['POST'])
def search_results():
    """Search for borrowers"""
    search_type = request.form.get('search_type')
    results = []
    search_params = dict(request.form)
    
    if search_type == 'criteria':
        # Criteria-based search
        criteria = {
            'village_city': request.form.get('village_city'),
            'taluka': request.form.get('taluka'),
            'district': request.form.get('district'),
            'bank_name': request.form.get('bank_name'),
            'reference': request.form.get('reference'),
            'borrower_name': request.form.get('borrower_name'),
            'co_borrower_name': request.form.get('co_borrower_name')
        }
        
        # Remove empty criteria
        criteria = {k: v for k, v in criteria.items() if v}
        
        if criteria:
            results = search_engine.search_borrowers(criteria)
    else:
        # Advanced search (text-based)
        search_text = request.form.get('search_text')
        if search_text:
            results = search_engine.advanced_search(search_text)
    
    options = borrower_manager.get_field_options()
    return render_template('search.html', 
                          results=results, 
                          search_params=search_params, 
                          options=options)


@app.route('/documents/<int:borrower_id>')
def documents(borrower_id):
    """Display documents for a borrower"""
    borrower = borrower_manager.get_borrower_by_id(borrower_id)
    
    if not borrower:
        flash('Borrower not found', 'danger')
        return redirect(url_for('index'))
    
    documents = document_handler.get_documents_for_borrower(borrower_id)
    
    return render_template('documents.html', 
                          borrower=borrower, 
                          documents=documents)


@app.route('/document/upload/<int:borrower_id>', methods=['GET', 'POST'])
def upload_document_route(borrower_id):
    """Upload a document for a borrower"""
    borrower = borrower_manager.get_borrower_by_id(borrower_id)
    
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
            filename = secure_filename(file.filename)
            description = request.form.get('description', '')
            
            # Save file to temporary location
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_path)
            
            # Upload document
            doc_id = document_handler.upload_document(borrower_id, temp_path, description)
            
            if doc_id:
                flash('Document uploaded successfully', 'success')
            else:
                flash('Failed to upload document', 'danger')
            
            return redirect(url_for('documents', borrower_id=borrower_id))
    
    return render_template('upload_document.html', borrower=borrower)


@app.route('/document/view/<int:doc_id>')
def view_document_route(doc_id):
    """View a document"""
    document = document_handler.get_document_by_id(doc_id)
    
    if not document:
        flash('Document not found', 'danger')
        return redirect(url_for('index'))
    
    # Get document path
    doc_path = os.path.join(app.config['UPLOAD_FOLDER'], document['filename'])
    
    if not os.path.exists(doc_path):
        flash('Document file not found', 'danger')
        return redirect(url_for('documents', borrower_id=document['borrower_id']))
    
    # Return the file
    return send_file(doc_path, 
                    download_name=document['original_filename'],
                    as_attachment=True)


@app.route('/document/delete/<int:doc_id>', methods=['POST'])
def delete_document_route(doc_id):
    """Delete a document"""
    document = document_handler.get_document_by_id(doc_id)
    
    if not document:
        flash('Document not found', 'danger')
        return redirect(url_for('index'))
    
    borrower_id = document['borrower_id']
    
    success = document_handler.delete_document(doc_id)
    
    if success:
        flash('Document deleted successfully', 'success')
    else:
        flash('Failed to delete document', 'danger')
    
    return redirect(url_for('documents', borrower_id=borrower_id))


@app.route('/export/all')
def export_all():
    """Export all borrowers to Excel"""
    borrowers = borrower_manager.get_all_borrowers()
    
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
    options = borrower_manager.get_field_options(field)
    return jsonify(options.get(field, []))


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error=error, title='Page Not Found', code=404), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error=error, title='Server Error', code=500), 500


# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)