#!/bin/bash

echo "Starting Maharashtra Lokadhikar Samiti Borrower Management System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed!"
    echo "Please install Python 3.7 or higher."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if this is the first run
if [ ! -d "venv" ]; then
    echo "First-time setup detected. Running easy installer..."
    echo ""
    python3 easy_install.py
else
    # Start the application with virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        python -m webbrowser -t "http://localhost:5000" &
        python app.py
        deactivate
    else
        # Fall back to system Python if venv activation fails
        python3 -m webbrowser -t "http://localhost:5000" &
        python3 app.py
    fi
fi

read -p "Press Enter to continue..."