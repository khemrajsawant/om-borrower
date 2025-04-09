#!/usr/bin/env python
"""
Maharashtra Lokadhikar Samiti - Borrower Management System
One-click installer script for non-technical users

This script provides an extremely simple way to install and run the application
with minimal user intervention. It handles all the necessary setup steps
and guides the user through the process with clear instructions.
"""
import os
import sys
import subprocess
import platform
import time
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
import shutil
import tempfile

# ANSI color codes for terminal output (Windows-compatible)
GREEN = '\033[92m' if platform.system() != "Windows" else ''
YELLOW = '\033[93m' if platform.system() != "Windows" else ''
RED = '\033[91m' if platform.system() != "Windows" else ''
BLUE = '\033[94m' if platform.system() != "Windows" else ''
ENDC = '\033[0m' if platform.system() != "Windows" else ''
BOLD = '\033[1m' if platform.system() != "Windows" else ''

# GUI Mode flag
GUI_MODE = True if len(sys.argv) > 1 and sys.argv[1] == "--gui" else False

def print_styled(style, message):
    """Print styled text that works across platforms."""
    if GUI_MODE:
        return  # Don't print to console in GUI mode
    if platform.system() == "Windows":
        print(message)
    else:
        print(f"{style}{message}{ENDC}")

def print_header(text):
    """Print a formatted header."""
    print_styled(f"{BLUE}{BOLD}", f"\n{'=' * 80}\n    {text}\n{'=' * 80}\n")

def print_step(text):
    """Print a step in the installation process."""
    print_styled(YELLOW, f"➤ {text}...")

def print_success(text):
    """Print a success message."""
    print_styled(GREEN, f"✓ {text}")

def print_error(text):
    """Print an error message."""
    print_styled(RED, f"✗ {text}")

def run_command(command, shell=False, show_output=False):
    """
    Run a shell command and return its output.
    
    Args:
        command: Command to run (list or string)
        shell: Whether to use shell execution
        show_output: Whether to print output in real-time
        
    Returns:
        Command output or None on failure
    """
    try:
        if show_output:
            # Run with live output display
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=shell,
                bufsize=1,
                universal_newlines=True
            )
            
            output = []
            for line in iter(process.stdout.readline, ''):
                output.append(line)
                print_styled('', line.strip())
                
            process.stdout.close()
            return_code = process.wait()
            
            if return_code:
                print_error(f"Command failed with exit code {return_code}")
                return None
            
            return ''.join(output)
        else:
            # Run without live output
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=shell
            )
            
            if result.returncode != 0:
                return None
                
            return result.stdout
    except Exception as e:
        print_error(f"Error running command: {str(e)}")
        return None

def check_python_version():
    """
    Check if Python is installed and has the correct version.
    
    Returns:
        bool: True if Python 3.7+ is installed
    """
    python_version = platform.python_version()
    version_parts = [int(x) for x in python_version.split('.')]
    
    if version_parts[0] < 3 or (version_parts[0] == 3 and version_parts[1] < 7):
        return False
    
    return True

def is_command_available(command):
    """
    Check if a command is available on the system.
    
    Args:
        command: Command name to check
        
    Returns:
        bool: True if the command is available
    """
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["where", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        else:
            result = subprocess.run(
                ["which", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        return result.returncode == 0
    except Exception:
        return False

def create_virtual_environment():
    """
    Create a Python virtual environment.
    
    Returns:
        str: Path to the virtual environment or None on failure
    """
    print_step("Creating virtual environment")
    
    if os.path.exists("venv"):
        print_success(f"Virtual environment already exists at {os.path.abspath('venv')}")
        return "venv"
    
    try:
        run_command([sys.executable, "-m", "venv", "venv"], show_output=True)
        print_success(f"Virtual environment created at {os.path.abspath('venv')}")
        return "venv"
    except Exception as e:
        print_error(f"Failed to create virtual environment: {str(e)}")
        return None

def install_dependencies(venv_path=None):
    """
    Install required Python dependencies.
    
    Args:
        venv_path: Path to virtual environment (optional)
        
    Returns:
        bool: True if successful
    """
    print_step("Installing dependencies")
    
    # Create requirements file if it doesn't exist
    if not os.path.exists("package_requirements.txt"):
        with open("package_requirements.txt", "w") as f:
            f.write("""flask==2.2.3
flask-sqlalchemy==3.0.3
openpyxl==3.1.2
pandas==2.0.0
psycopg2-binary==2.9.6
Werkzeug==2.2.3
python-dotenv==1.0.0
""")
        print_success("Created package_requirements.txt")
    
    try:
        if venv_path:
            # Use the virtual environment's pip
            pip_path = os.path.join(
                venv_path,
                "Scripts" if platform.system() == "Windows" else "bin",
                "pip"
            )
            run_command([pip_path, "install", "-r", "package_requirements.txt"], show_output=True)
        else:
            # Use the system's pip
            run_command([sys.executable, "-m", "pip", "install", "-r", "package_requirements.txt"], show_output=True)
        
        print_success("Dependencies installed successfully")
        return True
    except Exception as e:
        print_error(f"Failed to install dependencies: {str(e)}")
        return False

def setup_database():
    """
    Set up a local SQLite database.
    
    Returns:
        bool: True if successful
    """
    print_step("Setting up database")
    
    # Create data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
        print_success("Created data directory")
    
    # Create a .env file to store the database URL
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(f"""# Database configuration
DATABASE_URL=sqlite:///data/borrower_management.db

# Flask configuration
FLASK_ENV=development
FLASK_DEBUG=0

# Secret key for session security
FLASK_SECRET_KEY={os.urandom(24).hex()}
""")
        print_success("Created .env file with SQLite database configuration")
    
    # Initialize the database
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
        run_command([sys.executable, "init_db.py"], show_output=True)
        
        # Remove the temporary script
        os.remove("init_db.py")
        
        print_success("Database initialized successfully")
        return True
    except Exception as e:
        print_error(f"Failed to initialize database: {str(e)}")
        return False

def create_desktop_shortcut():
    """
    Create a desktop shortcut for the application.
    
    Returns:
        bool: True if successful
    """
    print_step("Creating desktop shortcut")
    
    try:
        # Get the current directory and the desktop directory
        app_path = os.path.abspath(os.path.dirname(__file__))
        desktop_dir = os.path.join(str(Path.home()), "Desktop")
        
        # Create the desktop directory if it doesn't exist
        if not os.path.exists(desktop_dir):
            os.makedirs(desktop_dir)
        
        os_type = platform.system()
        
        if os_type == "Windows":
            # Create a batch file for Windows
            shortcut_path = os.path.join(desktop_dir, "BorrowerManagementSystem.bat")
            
            with open(shortcut_path, 'w') as f:
                f.write('@echo off\n')
                f.write('echo Starting Maharashtra Lokadhikar Samiti Borrower Management System...\n')
                f.write(f'cd /d "{app_path}"\n')
                
                if os.path.exists("venv"):
                    # Use the virtual environment if it exists
                    f.write('call venv\\Scripts\\activate.bat\n')
                
                f.write('start http://localhost:5000\n')
                f.write('python app.py\n')
                
                if os.path.exists("venv"):
                    f.write('deactivate\n')
            
            print_success(f"Desktop shortcut created at: {shortcut_path}")
        
        elif os_type == "Linux":
            # Create a .desktop file for Linux
            shortcut_path = os.path.join(desktop_dir, "BorrowerManagementSystem.desktop")
            
            with open(shortcut_path, 'w') as f:
                f.write("[Desktop Entry]\n")
                f.write("Type=Application\n")
                f.write("Name=Borrower Management System\n")
                f.write("Comment=Maharashtra Lokadhikar Samiti Borrower Management System\n")
                
                if os.path.exists("venv"):
                    # Use the virtual environment if it exists
                    command = f'bash -c "cd {app_path} && source {os.path.join(app_path, "venv", "bin", "activate")} && python app.py"'
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
                f.write(f'cd "{app_path}"\n')
                
                if os.path.exists("venv"):
                    # Use the virtual environment if it exists
                    f.write(f'source "{os.path.join(app_path, "venv", "bin", "activate")}"\n')
                
                f.write(f'open http://localhost:5000\n')
                f.write(f'python app.py\n')
            
            # Make the script executable
            os.chmod(shortcut_path, 0o755)
            print_success(f"Desktop shortcut created at: {shortcut_path}")
        
        else:
            print_error(f"Unsupported operating system: {os_type}")
            return False
        
        return True
    except Exception as e:
        print_error(f"Failed to create desktop shortcut: {str(e)}")
        return False

def start_application():
    """
    Start the application and open the browser.
    
    Returns:
        subprocess.Popen: Process object for the running application
    """
    print_step("Starting application")
    print("Application will start in a moment. A browser window should open automatically.")
    print("Press Ctrl+C to stop the application.\n")
    
    # Open the browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:5000")
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run the application
    python_executable = sys.executable
    if os.path.exists("venv"):
        # Use the virtual environment's Python
        python_executable = os.path.join(
            "venv",
            "Scripts" if platform.system() == "Windows" else "bin",
            "python"
        )
    
    try:
        process = subprocess.Popen(
            [python_executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        return process
    except Exception as e:
        print_error(f"Failed to start application: {str(e)}")
        return None

class InstallerGUI:
    """GUI for the installer."""
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Borrower Management System - Easy Install")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Set icon if available
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "img", "favicon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="महाराष्ट्र लोकाधिकार समिती\nBorrower Management System", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Installation options frame
        options_frame = ttk.LabelFrame(main_frame, text="Installation Options", padding="10")
        options_frame.pack(fill=tk.BOTH, expand=True)
        
        # Checkboxes for installation options
        self.create_venv_var = tk.BooleanVar(value=True)
        create_venv_cb = ttk.Checkbutton(
            options_frame, 
            text="Create Virtual Environment (Recommended)", 
            variable=self.create_venv_var
        )
        create_venv_cb.pack(anchor=tk.W, pady=5)
        
        self.desktop_shortcut_var = tk.BooleanVar(value=True)
        desktop_shortcut_cb = ttk.Checkbutton(
            options_frame, 
            text="Create Desktop Shortcut", 
            variable=self.desktop_shortcut_var
        )
        desktop_shortcut_cb.pack(anchor=tk.W, pady=5)
        
        self.run_after_install_var = tk.BooleanVar(value=True)
        run_after_install_cb = ttk.Checkbutton(
            options_frame, 
            text="Run Application After Installation", 
            variable=self.run_after_install_var
        )
        run_after_install_cb.pack(anchor=tk.W, pady=5)
        
        # Progress frame
        self.progress_frame = ttk.LabelFrame(main_frame, text="Installation Progress", padding="10")
        self.progress_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            orient=tk.HORIZONTAL, 
            mode="determinate", 
            variable=self.progress_var
        )
        self.progress_bar.pack(fill=tk.X, pady=(10, 5))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to install")
        self.status_label = ttk.Label(
            self.progress_frame, 
            textvariable=self.status_var, 
            font=("Arial", 10)
        )
        self.status_label.pack(anchor=tk.W, pady=5)
        
        # Log text
        self.log_text = tk.Text(self.progress_frame, height=10, width=60, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self.log_text.config(state=tk.DISABLED)
        
        # Scrollbar for log text
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Install button
        self.install_button = ttk.Button(
            buttons_frame, 
            text="Install",
            command=self.start_installation
        )
        self.install_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Exit button
        self.exit_button = ttk.Button(
            buttons_frame, 
            text="Exit",
            command=self.root.destroy
        )
        self.exit_button.pack(side=tk.RIGHT)
    
    def log(self, message, level="info"):
        """Add a message to the log text."""
        self.log_text.config(state=tk.NORMAL)
        
        # Apply color based on log level
        if level == "error":
            tag = "error"
            self.log_text.tag_configure(tag, foreground="red")
        elif level == "success":
            tag = "success"
            self.log_text.tag_configure(tag, foreground="green")
        elif level == "warning":
            tag = "warning"
            self.log_text.tag_configure(tag, foreground="orange")
        else:
            tag = "info"
        
        # Add the message
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Update UI
        self.root.update_idletasks()
    
    def update_status(self, message, progress=None):
        """Update the status message and progress bar."""
        self.status_var.set(message)
        
        if progress is not None:
            self.progress_var.set(progress)
        
        # Update UI
        self.root.update_idletasks()
    
    def start_installation(self):
        """Start the installation process."""
        # Disable buttons during installation
        self.install_button.config(state=tk.DISABLED)
        
        # Clear log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Start installation in a separate thread
        install_thread = threading.Thread(target=self.run_installation)
        install_thread.daemon = True
        install_thread.start()
    
    def run_installation(self):
        """Run the installation process."""
        try:
            # Step 1: Check Python version
            self.update_status("Checking Python version...", 5)
            if not check_python_version():
                self.log("Error: Python 3.7 or higher is required.", "error")
                self.update_status("Installation failed: Python 3.7+ required", 0)
                self.install_button.config(state=tk.NORMAL)
                return
            self.log("Python version check passed.", "success")
            
            # Step 2: Create virtual environment (if selected)
            venv_path = None
            if self.create_venv_var.get():
                self.update_status("Creating virtual environment...", 20)
                if os.path.exists("venv"):
                    self.log("Virtual environment already exists.", "info")
                    venv_path = "venv"
                else:
                    self.log("Creating virtual environment...", "info")
                    try:
                        run_command([sys.executable, "-m", "venv", "venv"])
                        venv_path = "venv"
                        self.log("Virtual environment created successfully.", "success")
                    except Exception as e:
                        self.log(f"Error creating virtual environment: {str(e)}", "error")
                        self.update_status("Installation failed: Could not create virtual environment", 0)
                        self.install_button.config(state=tk.NORMAL)
                        return
            
            # Step 3: Install dependencies
            self.update_status("Installing dependencies...", 40)
            self.log("Installing dependencies...", "info")
            if not os.path.exists("package_requirements.txt"):
                self.log("Creating package_requirements.txt...", "info")
                with open("package_requirements.txt", "w") as f:
                    f.write("""flask==2.2.3
flask-sqlalchemy==3.0.3
openpyxl==3.1.2
pandas==2.0.0
psycopg2-binary==2.9.6
Werkzeug==2.2.3
python-dotenv==1.0.0
""")
            
            try:
                if venv_path:
                    # Use the virtual environment's pip
                    pip_path = os.path.join(
                        venv_path,
                        "Scripts" if platform.system() == "Windows" else "bin",
                        "pip"
                    )
                    result = run_command([pip_path, "install", "-r", "package_requirements.txt"])
                else:
                    # Use the system's pip
                    result = run_command([sys.executable, "-m", "pip", "install", "-r", "package_requirements.txt"])
                
                if result is None:
                    self.log("Error installing dependencies.", "error")
                    self.update_status("Installation failed: Could not install dependencies", 0)
                    self.install_button.config(state=tk.NORMAL)
                    return
                    
                self.log("Dependencies installed successfully.", "success")
            except Exception as e:
                self.log(f"Error installing dependencies: {str(e)}", "error")
                self.update_status("Installation failed: Could not install dependencies", 0)
                self.install_button.config(state=tk.NORMAL)
                return
            
            # Step 4: Set up database
            self.update_status("Setting up database...", 60)
            self.log("Setting up database...", "info")
            
            # Create data directory if it doesn't exist
            if not os.path.exists("data"):
                os.makedirs("data")
                self.log("Created data directory.", "info")
            
            # Create .env file if it doesn't exist
            if not os.path.exists(".env"):
                self.log("Creating .env file...", "info")
                with open(".env", "w") as f:
                    f.write(f"""# Database configuration
DATABASE_URL=sqlite:///data/borrower_management.db

# Flask configuration
FLASK_ENV=development
FLASK_DEBUG=0

# Secret key for session security
FLASK_SECRET_KEY={os.urandom(24).hex()}
""")
                self.log("Created .env file with SQLite database configuration.", "success")
            
            # Initialize the database
            self.log("Initializing database...", "info")
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
                python_executable = sys.executable
                if venv_path:
                    python_executable = os.path.join(
                        venv_path,
                        "Scripts" if platform.system() == "Windows" else "bin",
                        "python"
                    )
                
                result = run_command([python_executable, "init_db.py"])
                
                # Remove the temporary script
                os.remove("init_db.py")
                
                if result is None:
                    self.log("Error initializing database.", "error")
                    self.update_status("Installation failed: Could not initialize database", 0)
                    self.install_button.config(state=tk.NORMAL)
                    return
                
                self.log("Database initialized successfully.", "success")
            except Exception as e:
                self.log(f"Error initializing database: {str(e)}", "error")
                self.update_status("Installation failed: Could not initialize database", 0)
                self.install_button.config(state=tk.NORMAL)
                return
            
            # Step 5: Create desktop shortcut (if selected)
            if self.desktop_shortcut_var.get():
                self.update_status("Creating desktop shortcut...", 80)
                self.log("Creating desktop shortcut...", "info")
                if create_desktop_shortcut():
                    self.log("Desktop shortcut created successfully.", "success")
                else:
                    self.log("Error creating desktop shortcut.", "warning")
            
            # Installation complete
            self.update_status("Installation complete!", 100)
            self.log("Installation completed successfully.", "success")
            
            # Run the application (if selected)
            if self.run_after_install_var.get():
                self.log("Starting application...", "info")
                self.update_status("Starting application...", 100)
                
                # Start the application
                process = start_application()
                
                if process:
                    self.log("Application started successfully!", "success")
                    messagebox.showinfo(
                        "Installation Complete",
                        "Installation completed successfully!\n\n"
                        "The application has been started and should open in your web browser shortly."
                    )
                else:
                    self.log("Error starting application.", "error")
                    messagebox.showwarning(
                        "Installation Complete - Warning",
                        "Installation completed successfully, but there was an error starting the application.\n\n"
                        "Please try running the application manually using the desktop shortcut or by running 'python app.py'."
                    )
            else:
                messagebox.showinfo(
                    "Installation Complete",
                    "Installation completed successfully!\n\n"
                    "You can now run the application using the desktop shortcut or by running 'python app.py'."
                )
            
            # Re-enable the install button
            self.install_button.config(state=tk.NORMAL)
            
        except Exception as e:
            self.log(f"Error during installation: {str(e)}", "error")
            self.update_status("Installation failed", 0)
            self.install_button.config(state=tk.NORMAL)
            messagebox.showerror(
                "Installation Error",
                f"An error occurred during installation:\n\n{str(e)}"
            )

def console_installer():
    """Run the installer in console mode."""
    print_header("Maharashtra Lokadhikar Samiti Borrower Management System Easy Installer")
    
    # Check Python version
    print_step("Checking Python version")
    if not check_python_version():
        print_error("Python 3.7 or higher is required")
        return False
    print_success("Python version check passed")
    
    # Ask if user wants to create a virtual environment
    create_venv = input(f"\n{BOLD if platform.system() != 'Windows' else ''}Create virtual environment? (Recommended) [Y/n]: {ENDC if platform.system() != 'Windows' else ''}").lower() != "n"
    
    # Create virtual environment if requested
    venv_path = None
    if create_venv:
        venv_path = create_virtual_environment()
        if not venv_path:
            print("Continuing without virtual environment...")
    
    # Install dependencies
    if not install_dependencies(venv_path):
        return False
    
    # Set up database
    if not setup_database():
        return False
    
    # Ask if user wants to create a desktop shortcut
    create_shortcut = input(f"\n{BOLD if platform.system() != 'Windows' else ''}Create desktop shortcut? [Y/n]: {ENDC if platform.system() != 'Windows' else ''}").lower() != "n"
    
    # Create desktop shortcut if requested
    if create_shortcut:
        create_desktop_shortcut()
    
    # Installation complete
    print_header("Installation Complete!")
    
    # Ask if user wants to run the application now
    run_now = input(f"\n{BOLD if platform.system() != 'Windows' else ''}Run the application now? [Y/n]: {ENDC if platform.system() != 'Windows' else ''}").lower() != "n"
    
    # Run the application if requested
    if run_now:
        process = start_application()
        if not process:
            return False
        
        try:
            # Wait for the process to complete
            while True:
                try:
                    line = process.stdout.readline()
                    if not line:
                        break
                    print(line.rstrip())
                except KeyboardInterrupt:
                    # Handle Ctrl+C gracefully
                    print("\nStopping application...")
                    process.terminate()
                    process.wait()
                    break
        except Exception as e:
            print_error(f"Error while running application: {str(e)}")
            return False
    
    return True

def main():
    """Main function."""
    # Get the application path
    app_path = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the application directory
    os.chdir(app_path)
    
    if GUI_MODE:
        # Run the GUI installer
        root = tk.Tk()
        app = InstallerGUI(root)
        root.mainloop()
    else:
        # Run the console installer
        try:
            console_installer()
        except KeyboardInterrupt:
            print("\nInstallation canceled by user")
            sys.exit(1)
        except Exception as e:
            print_error(f"Error during installation: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()