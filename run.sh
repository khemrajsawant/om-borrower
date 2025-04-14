#!/bin/bash
echo "Starting Maharashtra Lokadhikar Samiti Borrower Management System..."
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
    python -m webbrowser -t "http://localhost:5000"
    python app.py
    deactivate
else
    python -m webbrowser -t "http://localhost:5000"
    python app.py
fi
