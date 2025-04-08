"""
Maharashtra Lokadhikar Samiti - Borrower Management System
Main application file that initializes the web application.
"""
from web_app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)