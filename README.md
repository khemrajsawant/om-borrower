# महाराष्ट्र लोकाधिकार समिती - Borrower Management System

A comprehensive system for managing borrower information, document tracking, and letter status management.

![Dashboard](static/img/logo.svg)

## Features

- **Borrower Management:** Add, edit, and delete borrower records with extensive field support
- **Document Handling:** Upload and manage multiple documents per borrower
- **Data Analysis:** View statistics and reports about borrowers and loan information
- **Export/Import:** Import and export data to Excel spreadsheets with Marathi language support
- **Advanced Search:** Search across multiple fields to quickly find borrower information
- **Letter Status Tracking:** Easily update and track the status of letters sent to borrowers

## Installation Guide

### 🔍 System Requirements

- Python 3.7 or higher
- Windows, macOS, or Linux operating system
- 2GB RAM minimum (4GB recommended)
- 500MB disk space

### 🚀 Super Easy Installation (Recommended)

#### Windows Users

1. Simply double-click the `start.bat` file
   - On first run, it will automatically install everything needed
   - On subsequent runs, it will just start the application

#### Mac and Linux Users

1. Open Terminal in the application folder
2. Run: `chmod +x start.sh` (first time only)
3. Run: `./start.sh`
   - On first run, it will automatically install everything needed
   - On subsequent runs, it will just start the application

### 💻 GUI Installer (Alternative)

For a graphical installation experience:

1. Open command prompt/terminal
2. Navigate to the application folder
3. Run: `python easy_install.py --gui`
4. Follow the on-screen instructions

### 🔧 Manual Installation Options

#### Option 1: Using run.py (Simplest)

```bash
# Start the application (auto-configures everything on first run)
python run.py
```

#### Option 2: Using setup.py (Interactive)

```bash
# Run the interactive setup wizard
python setup.py

# After setup completes, run the application
python app.py
```

#### Option 3: Manual Configuration

1. Copy `.env.example` to `.env` and edit as needed
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r package_requirements.txt`
5. Run the application: `python app.py`

## 📝 Usage Guide

1. **Add a Borrower:** Click the "Add Borrower" button on the dashboard
2. **Search Records:** Use the search box on any page or the advanced search feature
3. **Upload Documents:** When viewing a borrower record, use the documents section
4. **Export Data:** Click on stat cards on the dashboard to filter and export data
5. **Update Letter Status:** Edit a borrower to update letter status

## 📂 File Structure

```
/data                  - Database and data files
/static                - Static assets (CSS, JS, images)
/templates             - HTML templates
/uploads               - Uploaded documents
app.py                 - Main application entry point
models.py              - Database models
```

## 🔄 Database Configuration

The application uses SQLite by default, which requires no setup. For PostgreSQL:

1. Edit the `.env` file and update DATABASE_URL
2. Example: `DATABASE_URL=postgresql://username:password@localhost:5432/borrower_management`

## 🌐 Multilingual Support

- The application UI is in English
- Data entry supports Marathi using Unicode/UTF-8 encoding
- No additional configuration needed for Marathi text

## 💡 Troubleshooting

- **Application won't start:** Ensure Python 3.7+ is installed and in your PATH
- **Database errors:** Check your `.env` file for correct database configuration
- **Document upload issues:** Ensure the `/uploads` directory is writable

## 📞 Support

This software is proprietary and intended for use by Maharashtra Lokadhikar Samiti.

For technical support, please contact [support@example.com].