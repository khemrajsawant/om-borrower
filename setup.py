#!/usr/bin/env python
"""
Setup script for Maharashtra Lokadhikar Samiti Borrower Management System
This script automates the deployment process for local systems.
"""
import os
import sys
import subprocess
import platform
import getpass
import shutil
import webbrowser
from pathlib import Path
import time

# ANSI color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
ENDC = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{BLUE}{BOLD}{'=' * 80}{ENDC}")
    print(f"{BLUE}{BOLD}    {text}{ENDC}")
    print(f"{BLUE}{BOLD}{'=' * 80}{ENDC}\n")

def print_step(text):
    """Print a step in the installation process."""
    print(f"{YELLOW}➤ {text}...{ENDC}")

def print_success(text):
    """Print a success message."""
    print(f"{GREEN}✓ {text}{ENDC}")

def print_error(text):
    """Print an error message."""
    print(f"{RED}✗ {text}{ENDC}")

def run_command(command, shell=False):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=shell,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return None

def is_command_available(command):
    """Check if a command is available on the system."""
    try:
        subprocess.run(
            ["which" if platform.system() != "Windows" else "where", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def create_desktop_shortcut(app_path, venv_path=None):
    """Create a desktop shortcut for the application."""
    desktop_dir = os.path.join(str(Path.home()), "Desktop")
    os_type = platform.system()
    
    if os_type == "Windows":
        # Create a .bat file for Windows
        shortcut_path = os.path.join(desktop_dir, "BorrowerManagementSystem.bat")
        
        with open(shortcut_path, 'w') as f:
            if venv_path:
                # Use the virtual environment if provided
                f.write(f'@echo off\n')
                f.write(f'cd /d "{app_path}"\n')
                f.write(f'call "{os.path.join(venv_path, "Scripts", "activate.bat")}"\n')
                f.write(f'start http://localhost:5000\n')
                f.write(f'python app.py\n')
                f.write(f'deactivate\n')
            else:
                # Direct execution without virtual environment
                f.write(f'@echo off\n')
                f.write(f'cd /d "{app_path}"\n')
                f.write(f'start http://localhost:5000\n')
                f.write(f'python app.py\n')
        
        print_success(f"Desktop shortcut created at: {shortcut_path}")
    
    elif os_type == "Linux":
        # Create a .desktop file for Linux
        shortcut_path = os.path.join(desktop_dir, "BorrowerManagementSystem.desktop")
        
        with open(shortcut_path, 'w') as f:
            f.write("[Desktop Entry]\n")
            f.write("Type=Application\n")
            f.write("Name=Borrower Management System\n")
            f.write("Comment=Maharashtra Lokadhikar Samiti Borrower Management System\n")
            
            if venv_path:
                # Use the virtual environment if provided
                command = f'bash -c "cd {app_path} && source {os.path.join(venv_path, "bin", "activate")} && python app.py"'
            else:
                # Direct execution without virtual environment
                command = f'bash -c "cd {app_path} && python app.py"'
            
            f.write(f"Exec={command}\n")
            f.write("Terminal=true\n")
            f.write("Categories=Utility;\n")
        
        # Make the .desktop file executable
        os.chmod(shortcut_path, 0o755)
        print_success(f"Desktop shortcut created at: {shortcut_path}")
        
    elif os_type == "Darwin":  # macOS
        # Create an AppleScript file for macOS
        shortcut_path = os.path.join(desktop_dir, "BorrowerManagementSystem.command")
        
        with open(shortcut_path, 'w') as f:
            f.write("#!/bin/bash\n")
            
            if venv_path:
                # Use the virtual environment if provided
                f.write(f'cd "{app_path}"\n')
                f.write(f'source "{os.path.join(venv_path, "bin", "activate")}"\n')
                f.write(f'open http://localhost:5000\n')
                f.write(f'python app.py\n')
            else:
                # Direct execution without virtual environment
                f.write(f'cd "{app_path}"\n')
                f.write(f'open http://localhost:5000\n')
                f.write(f'python app.py\n')
        
        # Make the script executable
        os.chmod(shortcut_path, 0o755)
        print_success(f"Desktop shortcut created at: {shortcut_path}")
    
    else:
        print_error(f"Unsupported operating system: {os_type}")

def create_bundled_exe(app_path, venv_path=None):
    """Create a standalone executable using PyInstaller."""
    print_step("Creating standalone executable")
    
    try:
        # Ensure PyInstaller is installed
        if not is_command_available("pyinstaller"):
            if venv_path:
                # Install PyInstaller in the virtual environment
                run_command([
                    os.path.join(venv_path, "Scripts" if platform.system() == "Windows" else "bin", "pip"),
                    "install",
                    "pyinstaller"
                ])
            else:
                # Install PyInstaller globally
                run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])
                
        # Create a simple launcher script
        launcher_script = os.path.join(app_path, "launch.py")
        
        with open(launcher_script, 'w') as f:
            f.write("""#!/usr/bin/env python
import os
import sys
import subprocess
import webbrowser
import time

def main():
    # Start the Flask application
    flask_process = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a moment for the application to start
    time.sleep(2)
    
    # Open the browser
    webbrowser.open("http://localhost:5000")
    
    try:
        # Wait for the Flask application to exit
        flask_process.wait()
    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        flask_process.terminate()
        flask_process.wait()

if __name__ == "__main__":
    # Ensure working directory is set correctly
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
""")
        
        # Run PyInstaller
        pyinstaller_cmd = [
            "pyinstaller",
            "--name=BorrowerManagementSystem",
            "--onefile",
            "--add-data=templates;templates" if platform.system() == "Windows" else "--add-data=templates:templates",
            "--add-data=static;static" if platform.system() == "Windows" else "--add-data=static:static",
            "--hidden-import=flask",
            "--hidden-import=flask_sqlalchemy",
            "--hidden-import=openpyxl",
            "--hidden-import=pandas",
            "--hidden-import=psycopg2",
            launcher_script
        ]
        
        # Use the virtual environment's PyInstaller if available
        if venv_path and platform.system() == "Windows":
            pyinstaller_path = os.path.join(venv_path, "Scripts", "pyinstaller.exe")
            if os.path.exists(pyinstaller_path):
                pyinstaller_cmd[0] = pyinstaller_path
        elif venv_path:
            pyinstaller_path = os.path.join(venv_path, "bin", "pyinstaller")
            if os.path.exists(pyinstaller_path):
                pyinstaller_cmd[0] = pyinstaller_path
        
        # Change to the app directory
        original_dir = os.getcwd()
        os.chdir(app_path)
        
        # Run PyInstaller
        result = run_command(pyinstaller_cmd)
        
        # Change back to the original directory
        os.chdir(original_dir)
        
        if result is not None:
            print_success("Standalone executable created successfully")
            # Copy the executable to the desktop
            exe_path = os.path.join(app_path, "dist", "BorrowerManagementSystem.exe" if platform.system() == "Windows" else "BorrowerManagementSystem")
            desktop_path = os.path.join(str(Path.home()), "Desktop", "BorrowerManagementSystem.exe" if platform.system() == "Windows" else "BorrowerManagementSystem")
            
            if os.path.exists(exe_path):
                shutil.copy2(exe_path, desktop_path)
                if platform.system() != "Windows":
                    os.chmod(desktop_path, 0o755)
                print_success(f"Executable copied to desktop: {desktop_path}")
            else:
                print_error(f"Executable not found at: {exe_path}")
        else:
            print_error("Failed to create standalone executable")
    
    except Exception as e:
        print_error(f"Failed to create standalone executable: {str(e)}")

def setup_postgresql_locally():
    """Set up a local PostgreSQL database."""
    print_step("Setting up local PostgreSQL database")
    
    # # Check if PostgreSQL is already installed
    # if not is_command_available("psql"):
    #     print_error("PostgreSQL is not installed. Please install PostgreSQL first.")
    #     print(f"Visit {BLUE}https://www.postgresql.org/download/{ENDC} to download and install PostgreSQL.")
    #     return False
    
    # Get database configuration
    # db_user = input(f"\n{BOLD}Enter PostgreSQL username [{getpass.getuser()}]: {ENDC}") or getpass.getuser()
    # db_password = getpass.getpass(f"{BOLD}Enter PostgreSQL password: {ENDC}")
    # db_name = input(f"{BOLD}Enter database name [borrower_management]: {ENDC}") or "borrower_management"
    # db_host = input(f"{BOLD}Enter database host [localhost]: {ENDC}") or "localhost"
    # db_port = input(f"{BOLD}Enter database port [5432]: {ENDC}") or "5432"
    
    # Create database connection string
    # db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    db_url = "postgresql://admin:admin@my_postgres:5432/borrower_management"
    try:
        # # Create the database
        # run_command([
        #     "psql",
        #     "-c", f"CREATE DATABASE {db_name};",
        #     "-U", db_user,
        #     "-h", db_host,
        #     "-p", db_port
        # ])
        
        # Create a .env file to store the database URL
        with open(".env", "w") as f:
            f.write(f"DATABASE_URL={db_url}\n")
        
        print_success("PostgreSQL database set up successfully")
        return True
    
    except Exception as e:
        print_error(f"Failed to set up PostgreSQL database: {str(e)}")
        return False

def setup_sqlite_locally():
    """Set up a local SQLite database."""
    print_step("Setting up local SQLite database")
    
    # Create data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Create a .env file to store the database URL
    with open(".env", "w") as f:
        f.write("DATABASE_URL=sqlite:///data/borrower_management.db\n")
    
    print_success("SQLite database set up successfully")
    return True

def create_requirements_file():
    """Create a requirements.txt file."""
    print_step("Creating package_requirements.txt file")
    
    # Check if package_requirements.txt already exists
    if os.path.exists("package_requirements.txt"):
        print("package_requirements.txt file already exists")
        return
        
    with open("package_requirements.txt", "w") as f:
        f.write("""flask==2.2.3
flask-sqlalchemy==3.0.3
openpyxl==3.1.2
pandas==2.0.0
psycopg2-binary==2.9.6
Werkzeug==2.2.3
python-dotenv==1.0.0
""")
    
    print_success("package_requirements.txt file created")

def create_run_script():
    """Create a run script for the application."""
    print_step("Creating run script")
    
    if platform.system() == "Windows":
        # Create a batch file for Windows
        with open("run.bat", "w") as f:
            f.write("""@echo off
echo Starting Maharashtra Lokadhikar Samiti Borrower Management System...
if exist venv\\Scripts\\activate.bat (
    call venv\\Scripts\\activate.bat
    start http://localhost:5000
    python app.py
    deactivate
) else (
    start http://localhost:5000
    python app.py
)
""")
        os.chmod("run.bat", 0o755)
        print_success("run.bat script created")
    else:
        # Create a shell script for Unix-like systems
        with open("run.sh", "w") as f:
            f.write("""#!/bin/bash
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
""")
        os.chmod("run.sh", 0o755)
        print_success("run.sh script created")

def check_for_required_packages():
    """Check if Python and pip are installed and have correct versions."""
    print_step("Checking for required software")
    
    # Check Python version
    python_version = platform.python_version()
    print(f"Python version: {python_version}")
    
    if int(python_version.split('.')[0]) < 3 or (int(python_version.split('.')[0]) == 3 and int(python_version.split('.')[1]) < 7):
        print_error("Python 3.7 or higher is required")
        return False
    
    # Check if pip is installed
    try:
        pip_version = run_command([sys.executable, "-m", "pip", "--version"])
        if pip_version:
            print(f"pip is installed: {pip_version.strip()}")
        else:
            print_error("pip is not installed or not working properly")
            return False
    except Exception:
        print_error("pip is not installed or not working properly")
        return False
    
    print_success("All required software is installed")
    return True

def create_virtual_environment():
    """Create a Python virtual environment."""
    print_step("Creating virtual environment")
    
    if os.path.exists("venv"):
        print(f"Virtual environment already exists at {os.path.abspath('venv')}")
        return "venv"
    
    try:
        run_command([sys.executable, "-m", "venv", "venv"])
        print_success(f"Virtual environment created at {os.path.abspath('venv')}")
        return "venv"
    except Exception as e:
        print_error(f"Failed to create virtual environment: {str(e)}")
        return None

def install_dependencies(venv_path=None):
    """Install required Python dependencies."""
    print_step("Installing dependencies")
    
    # Create package_requirements.txt if it doesn't exist
    if not os.path.exists("package_requirements.txt"):
        create_requirements_file()
    
    try:
        if venv_path:
            # Use the virtual environment's pip
            pip_path = os.path.join(
                venv_path,
                "Scripts" if platform.system() == "Windows" else "bin",
                "pip"
            )
            run_command([pip_path, "install", "-r", "package_requirements.txt"])
        else:
            # Use the system's pip
            run_command([sys.executable, "-m", "pip", "install", "-r", "package_requirements.txt"])
        
        print_success("Dependencies installed successfully")
        return True
    except Exception as e:
        print_error(f"Failed to install dependencies: {str(e)}")
        return False

def initialize_database():
    """Initialize the database."""
    print_step("Initializing database")
    
    try:
        # Create a temporary script to initialize the database
        with open("init_db.py", "w") as f:
            f.write("""import os
from dotenv import load_dotenv
from app import app
from models import db

# Load environment variables
load_dotenv()

# Initialize the database
with app.app_context():
    db.create_all()
    print("Database initialized successfully")
""")
        
        # Run the script
        run_command([sys.executable, "init_db.py"])
        
        # Remove the temporary script
        os.remove("init_db.py")
        
        print_success("Database initialized successfully")
        return True
    except Exception as e:
        print_error(f"Failed to initialize database: {str(e)}")
        return False

def main():
    """Main setup function."""
    print_header("Maharashtra Lokadhikar Samiti Borrower Management System Setup")
    
    # Get the current directory
    app_path = os.path.abspath(os.path.dirname(__file__))
    print(f"Application path: {app_path}")
    
    # Check for required software
    if not check_for_required_packages():
        return
    
    # Create virtual environment
    venv_path = create_virtual_environment()
    
    # Install dependencies
    if not install_dependencies(venv_path):
        return
    
    # # Set up database
    # db_choice = "2"
    
    # if db_choice == "2":
    #     if not setup_postgresql_locally():
    #         print("Falling back to SQLite database...")
    #         setup_sqlite_locally()
    # else:
    #     setup_sqlite_locally()
    
    # # Initialize the database
    # if not initialize_database():
    #     return
    
    # # Create run script
    # create_run_script()
    
    # # Create desktop shortcut
    # create_shortcut = "no"
    # if create_shortcut:
    #     create_desktop_shortcut(app_path, venv_path)
    
    # # Create standalone executable
    # create_exe = "no"
    # if create_exe:
    #     create_bundled_exe(app_path, venv_path)
    
    # print_header("Setup Complete!")



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup canceled by user")
        sys.exit(1)