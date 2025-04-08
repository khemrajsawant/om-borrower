# महाराष्ट्र लोकाधिकार समिती - Borrower Management System

A comprehensive system for managing borrower information, document tracking, and letter status management.

## Features

- **Borrower Management:** Add, edit, and delete borrower records with extensive field support
- **Document Handling:** Upload and manage multiple documents per borrower
- **Data Analysis:** View statistics and reports about borrowers and loan information
- **Export/Import:** Import and export data to Excel spreadsheets with Marathi language support
- **Advanced Search:** Search across multiple fields to quickly find borrower information
- **Letter Status Tracking:** Easily update and track the status of letters sent to borrowers

## Technical Details

- Built with Python, Flask, and SQLAlchemy
- Supports both SQLite (for easy local deployment) and PostgreSQL (for production)
- Responsive web interface optimized for desktop use
- Multilingual support with special handling for Marathi script
- Document preview capabilities for common file formats

## Getting Started

### Quick Start

The easiest way to start the application:

```bash
# Clone the repository
git clone https://github.com/your-org/borrower-management.git
cd borrower-management

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r package_requirements.txt

# Start the application
python run.py
```

### Installation Options

#### 1. Simple Run Script

The `run.py` script provides a quick way to start the application without additional setup. It will:

- Create necessary directories
- Generate a default .env file if one doesn't exist
- Start the application and open your web browser

#### 2. Setup Script

For a more comprehensive setup, use the `setup.py` script:

```bash
python setup.py
```

This interactive script will:

- Check for required software
- Create a virtual environment
- Install dependencies
- Set up the database (SQLite or PostgreSQL)
- Create shortcuts or standalone executables (optional)

#### 3. Manual Configuration

1. Copy `.env.example` to `.env` and edit the configuration as needed
2. Install dependencies: `pip install -r package_requirements.txt`
3. Run the application: `python app.py`

## Configuration

- Database configuration can be modified in the `.env` file
- The application uses SQLite by default but can be configured to use PostgreSQL

## License

This software is proprietary and intended for use by Maharashtra Lokadhikar Samiti.

## Support

For support, please contact [support@example.com].