-- Database schema for the Borrower Management System

-- Borrowers table
CREATE TABLE IF NOT EXISTS borrowers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial_no INTEGER NOT NULL,
    date TEXT NOT NULL,
    reference TEXT,
    borrower_name TEXT NOT NULL,
    co_borrower_name TEXT,
    address_line1 TEXT NOT NULL,
    address_line2 TEXT,
    village_city TEXT NOT NULL,
    taluka TEXT,
    district TEXT NOT NULL,
    pin_code TEXT,
    mobile TEXT,
    bank_name TEXT,
    loan_amount TEXT,
    letter_status TEXT DEFAULT 'Not Send',
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    borrower_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    upload_date TEXT NOT NULL,
    description TEXT,
    file_type TEXT,
    FOREIGN KEY (borrower_id) REFERENCES borrowers (id) ON DELETE CASCADE
);

-- Index for borrowers
CREATE INDEX IF NOT EXISTS idx_borrower_serial_no ON borrowers (serial_no);
CREATE INDEX IF NOT EXISTS idx_borrower_name ON borrowers (borrower_name);
CREATE INDEX IF NOT EXISTS idx_village_city ON borrowers (village_city);
CREATE INDEX IF NOT EXISTS idx_taluka ON borrowers (taluka);
CREATE INDEX IF NOT EXISTS idx_district ON borrowers (district);
CREATE INDEX IF NOT EXISTS idx_bank_name ON borrowers (bank_name);

-- Index for documents
CREATE INDEX IF NOT EXISTS idx_document_borrower_id ON documents (borrower_id);
