#!/usr/bin/env python
"""
Maharashtra Lokadhikar Samiti - Borrower Management System
Simple standalone launcher that opens the browser and starts the application
"""
import os
import sys
import webbrowser
import time
import subprocess
import platform
from pathlib import Path

def ensure_dir_exists(dir_path):
    """Ensure a directory exists."""
    os.makedirs(dir_path, exist_ok=True)

def get_python_executable():
    """Get the path to the Python executable."""
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment
        if platform.system() == "Windows":
            return os.path.join(sys.prefix, "Scripts", "python.exe")
        else:
            return os.path.join(sys.prefix, "bin", "python")
    else:
        # We're not in a virtual environment
        return sys.executable

def main():
    """Main function to start the application."""
    print("Starting Maharashtra Lokadhikar Samiti Borrower Management System...")
    
    # Change to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check if the data directory exists, create it if not
    data_dir = os.path.join(script_dir, "data")
    ensure_dir_exists(data_dir)
    
    # Create a default .env file if it doesn't exist
    env_path = os.path.join(script_dir, ".env")
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write(f"""# Database configuration
DATABASE_URL=sqlite:///data/borrower_management.db

# Flask configuration
FLASK_ENV=development
FLASK_DEBUG=1

# Secret key for session security
FLASK_SECRET_KEY={os.urandom(24).hex()}
""")
        print("Created default .env file with SQLite database configuration")
    
    # Start the application
    python_executable = get_python_executable()
    app_path = os.path.join(script_dir, "app.py")
    
    # Open the browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:5000")
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run the application
    try:
        subprocess.run([python_executable, app_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting the application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()