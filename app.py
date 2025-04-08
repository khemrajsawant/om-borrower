"""
Maharashtra Lokadhikar Samiti - Borrower Management System
Main application file that initializes the desktop application.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.font import Font
import sqlite3
from datetime import datetime

from database import init_db, get_db_connection
from borrower_manager import (
    add_borrower, update_borrower, delete_borrower, 
    get_borrower_by_id, get_all_borrowers, get_field_options
)
from document_handler import upload_document, get_documents_for_borrower
from excel_handler import export_to_excel, import_from_excel
from search_engine import search_borrowers
from ui_components import Calendar, ValidatingEntry, ScrollableFrame

class BorrowerManagementApp:
    """Main application class for the Borrower Management System."""

    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("Maharashtra Lokadhikar Samiti - Borrower Management System")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Initialize database
        init_db()
        
        # Setup UI fonts
        self.setup_fonts()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Setup tabs
        self.setup_tabs()
        
        # Setup menu
        self.setup_menu()
        
        # Initialize variables
        self.current_borrower_id = None
        self.search_results = []
        
        # Load initial data
        self.load_data()

    def setup_fonts(self):
        """Setup fonts for the application."""
        self.header_font = Font(family="Arial", size=12, weight="bold")
        self.normal_font = Font(family="Arial", size=10)
        self.devanagari_font = Font(family="Nirmala UI", size=10)  # Font for Marathi

    def setup_tabs(self):
        """Setup tab structure for the application."""
        self.tab_control = ttk.Notebook(self.main_frame)
        
        # Borrower list tab
        self.tab_list = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_list, text="Borrower List")
        self.setup_list_tab()
        
        # Add/Edit borrower tab
        self.tab_form = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_form, text="Add/Edit Borrower")
        self.setup_form_tab()
        
        # Search tab
        self.tab_search = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_search, text="Search")
        self.setup_search_tab()
        
        # Documents tab
        self.tab_docs = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_docs, text="Documents")
        self.setup_documents_tab()
        
        self.tab_control.pack(expand=1, fill="both")

    def setup_menu(self):
        """Setup the application menu."""
        self.menu_bar = tk.Menu(self.root)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Export to Excel", command=self.export_data)
        self.file_menu.add_command(label="Import from Excel", command=self.import_data)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        
        self.root.config(menu=self.menu_bar)

    def setup_list_tab(self):
        """Setup the borrower list tab."""
        # Create frame for controls
        self.list_controls_frame = ttk.Frame(self.tab_list, padding="5")
        self.list_controls_frame.pack(fill=tk.X, side=tk.TOP)
        
        # Add refresh button
        self.refresh_btn = ttk.Button(self.list_controls_frame, text="Refresh List", command=self.load_borrowers)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Create treeview for borrower list
        self.borrower_tree_frame = ttk.Frame(self.tab_list)
        self.borrower_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree_columns = (
            "serial_no", "date", "reference", "name", "co_borrower", 
            "village_city", "taluka", "district", "bank_name", "loan_amount", "letter_status"
        )
        self.borrower_tree = ttk.Treeview(
            self.borrower_tree_frame, 
            columns=self.tree_columns,
            show="headings",
            selectmode="browse"
        )
        
        # Configure columns and headings
        self.borrower_tree.heading("serial_no", text="Sr. No")
        self.borrower_tree.heading("date", text="Date")
        self.borrower_tree.heading("reference", text="Reference")
        self.borrower_tree.heading("name", text="Borrower Name")
        self.borrower_tree.heading("co_borrower", text="Co-Borrower")
        self.borrower_tree.heading("village_city", text="Village/City")
        self.borrower_tree.heading("taluka", text="Taluka")
        self.borrower_tree.heading("district", text="District")
        self.borrower_tree.heading("bank_name", text="Bank Name")
        self.borrower_tree.heading("loan_amount", text="Loan Amount")
        self.borrower_tree.heading("letter_status", text="Letter Status")
        
        # Set column widths
        self.borrower_tree.column("serial_no", width=60)
        self.borrower_tree.column("date", width=100)
        self.borrower_tree.column("reference", width=120)
        self.borrower_tree.column("name", width=150)
        self.borrower_tree.column("co_borrower", width=150)
        self.borrower_tree.column("village_city", width=120)
        self.borrower_tree.column("taluka", width=100)
        self.borrower_tree.column("district", width=100)
        self.borrower_tree.column("bank_name", width=120)
        self.borrower_tree.column("loan_amount", width=100)
        self.borrower_tree.column("letter_status", width=100)
        
        # Add vertical scrollbar
        tree_scrollbar = ttk.Scrollbar(
            self.borrower_tree_frame, 
            orient="vertical", 
            command=self.borrower_tree.yview
        )
        self.borrower_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Add horizontal scrollbar
        tree_h_scrollbar = ttk.Scrollbar(
            self.borrower_tree_frame, 
            orient="horizontal", 
            command=self.borrower_tree.xview
        )
        self.borrower_tree.configure(xscrollcommand=tree_h_scrollbar.set)
        
        # Pack the tree and scrollbars
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.borrower_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.borrower_tree.bind("<<TreeviewSelect>>", self.on_borrower_select)
        
        # Add buttons for actions
        self.list_actions_frame = ttk.Frame(self.tab_list, padding="5")
        self.list_actions_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.edit_btn = ttk.Button(self.list_actions_frame, text="Edit", command=self.edit_borrower)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(self.list_actions_frame, text="Delete", command=self.confirm_delete)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.view_docs_btn = ttk.Button(self.list_actions_frame, text="View Documents", command=self.view_documents)
        self.view_docs_btn.pack(side=tk.LEFT, padx=5)

    def setup_form_tab(self):
        """Setup the borrower form tab for adding and editing borrowers."""
        # Use ScrollableFrame for the form
        self.form_scroll = ScrollableFrame(self.tab_form)
        self.form_scroll.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.form_frame = self.form_scroll.scrolled_frame
        
        # Setup form fields
        self.setup_form_fields()
        
        # Form action buttons
        self.form_buttons_frame = ttk.Frame(self.form_frame, padding="5")
        self.form_buttons_frame.grid(row=17, column=0, columnspan=4, sticky="ew", pady=10)
        
        self.save_btn = ttk.Button(self.form_buttons_frame, text="Save", command=self.save_borrower)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(self.form_buttons_frame, text="Clear Form", command=self.clear_form)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.cancel_btn = ttk.Button(self.form_buttons_frame, text="Cancel", command=self.cancel_edit)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

    def setup_form_fields(self):
        """Setup the form fields for borrower data entry."""
        # Form title
        self.form_title = ttk.Label(
            self.form_frame, text="Borrower Information", font=self.header_font
        )
        self.form_title.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))
        
        # Field Variables
        self.var_serial_no = tk.StringVar()
        self.var_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.var_reference = tk.StringVar()
        self.var_borrower_name = tk.StringVar()
        self.var_co_borrower_name = tk.StringVar()
        self.var_address_line1 = tk.StringVar()
        self.var_address_line2 = tk.StringVar()
        self.var_village_city = tk.StringVar()
        self.var_taluka = tk.StringVar()
        self.var_district = tk.StringVar()
        self.var_pin_code = tk.StringVar()
        self.var_mobile = tk.StringVar()
        self.var_bank_name = tk.StringVar()
        self.var_loan_amount = tk.StringVar()
        self.var_letter_status = tk.StringVar(value="Not Send")
        self.var_notes = tk.StringVar()
        
        # Serial Number (read-only)
        ttk.Label(self.form_frame, text="Serial No:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.serial_no_entry = ttk.Entry(self.form_frame, textvariable=self.var_serial_no, state="readonly", width=10)
        self.serial_no_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Date
        ttk.Label(self.form_frame, text="Date:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.date_frame = ttk.Frame(self.form_frame)
        self.date_frame.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        self.date_entry = ttk.Entry(self.date_frame, textvariable=self.var_date, width=12)
        self.date_entry.pack(side=tk.LEFT)
        self.date_button = ttk.Button(
            self.date_frame, text="📅", width=3,
            command=lambda: self.pick_date(self.var_date)
        )
        self.date_button.pack(side=tk.LEFT)
        
        # Reference
        ttk.Label(self.form_frame, text="Reference:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.reference_combo = ttk.Combobox(
            self.form_frame, textvariable=self.var_reference, width=30
        )
        self.reference_combo.grid(row=2, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Borrower Name
        ttk.Label(self.form_frame, text="Full Name of Borrower:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.borrower_name_entry = ttk.Entry(
            self.form_frame, textvariable=self.var_borrower_name, width=40, font=self.devanagari_font
        )
        self.borrower_name_entry.grid(row=3, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Co-Borrower Name
        ttk.Label(self.form_frame, text="Full Name of Co-Borrower:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.co_borrower_entry = ttk.Entry(
            self.form_frame, textvariable=self.var_co_borrower_name, width=40, font=self.devanagari_font
        )
        self.co_borrower_entry.grid(row=4, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Address Line 1
        ttk.Label(self.form_frame, text="Address Line 1:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.addr1_entry = ttk.Entry(
            self.form_frame, textvariable=self.var_address_line1, width=60, font=self.devanagari_font
        )
        self.addr1_entry.grid(row=5, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Address Line 2
        ttk.Label(self.form_frame, text="Address Line 2:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.addr2_entry = ttk.Entry(
            self.form_frame, textvariable=self.var_address_line2, width=60, font=self.devanagari_font
        )
        self.addr2_entry.grid(row=6, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Village/City
        ttk.Label(self.form_frame, text="Village/City:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.village_city_combo = ttk.Combobox(
            self.form_frame, textvariable=self.var_village_city, width=30, font=self.devanagari_font
        )
        self.village_city_combo.grid(row=7, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Taluka
        ttk.Label(self.form_frame, text="Taluka:").grid(row=8, column=0, sticky="w", padx=5, pady=5)
        self.taluka_combo = ttk.Combobox(
            self.form_frame, textvariable=self.var_taluka, width=30, font=self.devanagari_font
        )
        self.taluka_combo.grid(row=8, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        # District
        ttk.Label(self.form_frame, text="District:").grid(row=9, column=0, sticky="w", padx=5, pady=5)
        self.district_combo = ttk.Combobox(
            self.form_frame, textvariable=self.var_district, width=30, font=self.devanagari_font
        )
        self.district_combo.grid(row=9, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Pin Code
        ttk.Label(self.form_frame, text="Pin Code:").grid(row=10, column=0, sticky="w", padx=5, pady=5)
        self.pin_entry = ValidatingEntry(
            self.form_frame, textvariable=self.var_pin_code, width=10,
            validate_func=lambda s: s.isdigit() and len(s) <= 6
        )
        self.pin_entry.grid(row=10, column=1, sticky="w", padx=5, pady=5)
        
        # Mobile Number
        ttk.Label(self.form_frame, text="Mobile No:").grid(row=10, column=2, sticky="w", padx=5, pady=5)
        self.mobile_entry = ValidatingEntry(
            self.form_frame, textvariable=self.var_mobile, width=15,
            validate_func=lambda s: s.isdigit() and len(s) <= 10
        )
        self.mobile_entry.grid(row=10, column=3, sticky="w", padx=5, pady=5)
        
        # Bank Name
        ttk.Label(self.form_frame, text="Bank Name:").grid(row=11, column=0, sticky="w", padx=5, pady=5)
        self.bank_combo = ttk.Combobox(
            self.form_frame, textvariable=self.var_bank_name, width=30, font=self.devanagari_font
        )
        self.bank_combo.grid(row=11, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Loan Amount
        ttk.Label(self.form_frame, text="Loan Amount:").grid(row=12, column=0, sticky="w", padx=5, pady=5)
        self.loan_entry = ValidatingEntry(
            self.form_frame, textvariable=self.var_loan_amount, width=20,
            validate_func=lambda s: all(c.isdigit() or c == '.' for c in s)
        )
        self.loan_entry.grid(row=12, column=1, sticky="w", padx=5, pady=5)
        
        # Letter Status
        ttk.Label(self.form_frame, text="Letter Status:").grid(row=12, column=2, sticky="w", padx=5, pady=5)
        self.letter_combo = ttk.Combobox(
            self.form_frame, textvariable=self.var_letter_status, width=20,
            values=["Not Send", "Send", "Returned Back"]
        )
        self.letter_combo.grid(row=12, column=3, sticky="w", padx=5, pady=5)
        
        # Notes
        ttk.Label(self.form_frame, text="Notes:").grid(row=13, column=0, sticky="nw", padx=5, pady=5)
        self.notes_text = tk.Text(self.form_frame, height=5, width=60, font=self.devanagari_font)
        self.notes_text.grid(row=13, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Load dropdown options
        self.load_dropdown_options()

    def setup_search_tab(self):
        """Setup the search tab for finding borrowers."""
        # Create search criteria frame
        self.search_frame = ttk.LabelFrame(self.tab_search, text="Search Criteria")
        self.search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Search variables
        self.search_var_village = tk.StringVar()
        self.search_var_taluka = tk.StringVar()
        self.search_var_district = tk.StringVar()
        self.search_var_bank = tk.StringVar()
        self.search_var_name = tk.StringVar()
        self.search_var_reference = tk.StringVar()
        
        # Village/City search
        ttk.Label(self.search_frame, text="Village/City:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.search_village_combo = ttk.Combobox(
            self.search_frame, textvariable=self.search_var_village, width=25, font=self.devanagari_font
        )
        self.search_village_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Taluka search
        ttk.Label(self.search_frame, text="Taluka:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.search_taluka_combo = ttk.Combobox(
            self.search_frame, textvariable=self.search_var_taluka, width=25, font=self.devanagari_font
        )
        self.search_taluka_combo.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # District search
        ttk.Label(self.search_frame, text="District:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.search_district_combo = ttk.Combobox(
            self.search_frame, textvariable=self.search_var_district, width=25, font=self.devanagari_font
        )
        self.search_district_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Bank Name search
        ttk.Label(self.search_frame, text="Bank Name:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.search_bank_combo = ttk.Combobox(
            self.search_frame, textvariable=self.search_var_bank, width=25, font=self.devanagari_font
        )
        self.search_bank_combo.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        # Borrower Name search
        ttk.Label(self.search_frame, text="Borrower Name:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.search_name_entry = ttk.Entry(
            self.search_frame, textvariable=self.search_var_name, width=25, font=self.devanagari_font
        )
        self.search_name_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Reference search
        ttk.Label(self.search_frame, text="Reference:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.search_reference_combo = ttk.Combobox(
            self.search_frame, textvariable=self.search_var_reference, width=25
        )
        self.search_reference_combo.grid(row=2, column=3, sticky="w", padx=5, pady=5)
        
        # Search button
        self.search_buttons_frame = ttk.Frame(self.search_frame)
        self.search_buttons_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        self.search_btn = ttk.Button(self.search_buttons_frame, text="Search", command=self.perform_search)
        self.search_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_search_btn = ttk.Button(self.search_buttons_frame, text="Clear", command=self.clear_search)
        self.clear_search_btn.pack(side=tk.LEFT, padx=5)
        
        # Search results
        self.search_results_frame = ttk.LabelFrame(self.tab_search, text="Search Results")
        self.search_results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for search results
        self.search_tree_frame = ttk.Frame(self.search_results_frame)
        self.search_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.search_tree = ttk.Treeview(
            self.search_tree_frame, 
            columns=self.tree_columns,
            show="headings",
            selectmode="browse"
        )
        
        # Configure columns and headings (same as borrower list)
        for col in self.tree_columns:
            self.search_tree.heading(col, text=col.replace("_", " ").title())
            self.search_tree.column(col, width=100)
        
        # Add vertical scrollbar
        search_tree_scrollbar = ttk.Scrollbar(
            self.search_tree_frame, 
            orient="vertical", 
            command=self.search_tree.yview
        )
        self.search_tree.configure(yscrollcommand=search_tree_scrollbar.set)
        
        # Add horizontal scrollbar
        search_tree_h_scrollbar = ttk.Scrollbar(
            self.search_tree_frame, 
            orient="horizontal", 
            command=self.search_tree.xview
        )
        self.search_tree.configure(xscrollcommand=search_tree_h_scrollbar.set)
        
        # Pack the tree and scrollbars
        search_tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        search_tree_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind select event
        self.search_tree.bind("<<TreeviewSelect>>", self.on_search_result_select)
        
        # Search result actions
        self.search_actions_frame = ttk.Frame(self.tab_search)
        self.search_actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.view_selected_btn = ttk.Button(
            self.search_actions_frame, text="View Selected", command=self.view_selected_borrower
        )
        self.view_selected_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_results_btn = ttk.Button(
            self.search_actions_frame, text="Export Results", command=self.export_search_results
        )
        self.export_results_btn.pack(side=tk.LEFT, padx=5)

    def setup_documents_tab(self):
        """Setup the documents tab for managing loan documents."""
        # Create two frames: left for borrower selection, right for document list
        self.docs_paned = ttk.PanedWindow(self.tab_docs, orient=tk.HORIZONTAL)
        self.docs_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Borrower selection frame
        self.docs_borrowers_frame = ttk.LabelFrame(self.docs_paned, text="Borrowers")
        self.docs_paned.add(self.docs_borrowers_frame, weight=40)
        
        # Create listbox for borrowers
        self.docs_borrowers_listbox_frame = ttk.Frame(self.docs_borrowers_frame)
        self.docs_borrowers_listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.docs_borrowers_listbox = tk.Listbox(
            self.docs_borrowers_listbox_frame, font=self.devanagari_font
        )
        self.docs_borrowers_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        docs_borrowers_scrollbar = ttk.Scrollbar(
            self.docs_borrowers_listbox_frame, 
            orient="vertical", 
            command=self.docs_borrowers_listbox.yview
        )
        self.docs_borrowers_listbox.configure(yscrollcommand=docs_borrowers_scrollbar.set)
        docs_borrowers_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add search field for borrowers
        self.docs_search_frame = ttk.Frame(self.docs_borrowers_frame)
        self.docs_search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.docs_search_var = tk.StringVar()
        self.docs_search_var.trace("w", self.filter_docs_borrowers)
        
        ttk.Label(self.docs_search_frame, text="Search:").pack(side=tk.LEFT)
        self.docs_search_entry = ttk.Entry(
            self.docs_search_frame, textvariable=self.docs_search_var
        )
        self.docs_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Bind selection event
        self.docs_borrowers_listbox.bind("<<ListboxSelect>>", self.on_docs_borrower_select)
        
        # Documents frame
        self.docs_list_frame = ttk.LabelFrame(self.docs_paned, text="Documents")
        self.docs_paned.add(self.docs_list_frame, weight=60)
        
        # Create treeview for documents
        self.docs_tree_frame = ttk.Frame(self.docs_list_frame)
        self.docs_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.docs_tree_columns = ("id", "filename", "upload_date", "description")
        self.docs_tree = ttk.Treeview(
            self.docs_tree_frame, 
            columns=self.docs_tree_columns,
            show="headings"
        )
        
        # Configure columns and headings
        self.docs_tree.heading("id", text="ID")
        self.docs_tree.heading("filename", text="Filename")
        self.docs_tree.heading("upload_date", text="Upload Date")
        self.docs_tree.heading("description", text="Description")
        
        self.docs_tree.column("id", width=50)
        self.docs_tree.column("filename", width=200)
        self.docs_tree.column("upload_date", width=100)
        self.docs_tree.column("description", width=300)
        
        # Add vertical scrollbar
        docs_tree_scrollbar = ttk.Scrollbar(
            self.docs_tree_frame, 
            orient="vertical", 
            command=self.docs_tree.yview
        )
        self.docs_tree.configure(yscrollcommand=docs_tree_scrollbar.set)
        docs_tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.docs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind double-click to open document
        self.docs_tree.bind("<Double-1>", self.open_document)
        
        # Document actions
        self.docs_actions_frame = ttk.Frame(self.docs_list_frame)
        self.docs_actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.upload_doc_btn = ttk.Button(
            self.docs_actions_frame, text="Upload Document", command=self.upload_new_document
        )
        self.upload_doc_btn.pack(side=tk.LEFT, padx=5)
        
        self.view_doc_btn = ttk.Button(
            self.docs_actions_frame, text="View Document", command=self.view_document
        )
        self.view_doc_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_doc_btn = ttk.Button(
            self.docs_actions_frame, text="Delete Document", command=self.delete_document
        )
        self.delete_doc_btn.pack(side=tk.LEFT, padx=5)

    def load_data(self):
        """Load initial data for the application."""
        # Load borrowers list
        self.load_borrowers()
        
        # Load dropdown options
        self.load_dropdown_options()
        
        # Initialize docs borrowers list
        self.load_docs_borrowers()
        
        # Load search dropdowns
        self.load_search_dropdowns()

    def load_borrowers(self):
        """Load all borrowers into the treeview."""
        # Clear existing items
        for item in self.borrower_tree.get_children():
            self.borrower_tree.delete(item)
        
        # Get all borrowers
        borrowers = get_all_borrowers()
        
        # Add to treeview
        for borrower in borrowers:
            values = (
                borrower["serial_no"],
                borrower["date"],
                borrower["reference"],
                borrower["borrower_name"],
                borrower["co_borrower_name"],
                borrower["village_city"],
                borrower["taluka"],
                borrower["district"],
                borrower["bank_name"],
                borrower["loan_amount"],
                borrower["letter_status"]
            )
            self.borrower_tree.insert("", "end", iid=borrower["id"], values=values)

    def load_dropdown_options(self):
        """Load options for dropdown menus."""
        # Get options from database
        options = get_field_options()
        
        # Set values for dropdowns
        self.reference_combo["values"] = options["reference"]
        self.village_city_combo["values"] = options["village_city"]
        self.taluka_combo["values"] = options["taluka"]
        self.district_combo["values"] = options["district"]
        self.bank_combo["values"] = options["bank_name"]

    def load_search_dropdowns(self):
        """Load options for search dropdown menus."""
        # Get options from database
        options = get_field_options()
        
        # Set values for search dropdowns
        self.search_village_combo["values"] = options["village_city"]
        self.search_taluka_combo["values"] = options["taluka"]
        self.search_district_combo["values"] = options["district"]
        self.search_bank_combo["values"] = options["bank_name"]
        self.search_reference_combo["values"] = options["reference"]

    def load_docs_borrowers(self):
        """Load borrowers into the documents tab listbox."""
        # Clear existing items
        self.docs_borrowers_listbox.delete(0, tk.END)
        
        # Get all borrowers
        borrowers = get_all_borrowers()
        
        # Add to listbox
        for borrower in borrowers:
            self.docs_borrowers_listbox.insert(
                tk.END, 
                f"{borrower['serial_no']} - {borrower['borrower_name']}"
            )
            # Store borrower ID in the listbox item
            self.docs_borrowers_listbox.itemconfig(
                tk.END, {"borrower_id": borrower["id"]}
            )

    def filter_docs_borrowers(self, *args):
        """Filter borrowers in documents tab based on search text."""
        search_text = self.docs_search_var.get().lower()
        
        # Clear existing items
        self.docs_borrowers_listbox.delete(0, tk.END)
        
        # Get all borrowers
        borrowers = get_all_borrowers()
        
        # Add matching borrowers to listbox
        for borrower in borrowers:
            if (search_text in str(borrower["serial_no"]).lower() or
                search_text in borrower["borrower_name"].lower()):
                self.docs_borrowers_listbox.insert(
                    tk.END, 
                    f"{borrower['serial_no']} - {borrower['borrower_name']}"
                )
                # Store borrower ID in the listbox item
                self.docs_borrowers_listbox.itemconfig(
                    tk.END, {"borrower_id": borrower["id"]}
                )

    def on_borrower_select(self, event):
        """Handle borrower selection in the main list."""
        selected_items = self.borrower_tree.selection()
        if selected_items:
            self.current_borrower_id = selected_items[0]

    def on_search_result_select(self, event):
        """Handle borrower selection in search results."""
        selected_items = self.search_tree.selection()
        if selected_items:
            # Find the borrower_id from selection
            selected_idx = int(selected_items[0])
            if 0 <= selected_idx < len(self.search_results):
                self.current_borrower_id = self.search_results[selected_idx]["id"]

    def on_docs_borrower_select(self, event):
        """Handle borrower selection in documents tab."""
        selected_idx = self.docs_borrowers_listbox.curselection()
        if selected_idx:
            # Get the borrower_id from the selected item
            borrower_id = self.docs_borrowers_listbox.itemcget(selected_idx[0], "borrower_id")
            self.load_documents_for_borrower(borrower_id)

    def edit_borrower(self):
        """Load borrower data into the form for editing."""
        if not self.current_borrower_id:
            messagebox.showinfo("Select a Borrower", "Please select a borrower to edit.")
            return
        
        # Get borrower data
        borrower = get_borrower_by_id(self.current_borrower_id)
        if not borrower:
            messagebox.showerror("Error", "Failed to load borrower data.")
            return
        
        # Switch to form tab
        self.tab_control.select(self.tab_form)
        
        # Fill form with borrower data
        self.clear_form()
        self.var_serial_no.set(borrower["serial_no"])
        self.var_date.set(borrower["date"])
        self.var_reference.set(borrower["reference"])
        self.var_borrower_name.set(borrower["borrower_name"])
        self.var_co_borrower_name.set(borrower["co_borrower_name"])
        self.var_address_line1.set(borrower["address_line1"])
        self.var_address_line2.set(borrower["address_line2"])
        self.var_village_city.set(borrower["village_city"])
        self.var_taluka.set(borrower["taluka"])
        self.var_district.set(borrower["district"])
        self.var_pin_code.set(borrower["pin_code"])
        self.var_mobile.set(borrower["mobile"])
        self.var_bank_name.set(borrower["bank_name"])
        self.var_loan_amount.set(borrower["loan_amount"])
        self.var_letter_status.set(borrower["letter_status"])
        
        # Set notes
        self.notes_text.delete("1.0", tk.END)
        self.notes_text.insert("1.0", borrower["notes"])
        
        # Update form title
        self.form_title.config(text=f"Edit Borrower: {borrower['borrower_name']}")

    def clear_form(self):
        """Clear the borrower form."""
        self.current_borrower_id = None
        self.var_serial_no.set("")
        self.var_date.set(datetime.now().strftime("%Y-%m-%d"))
        self.var_reference.set("")
        self.var_borrower_name.set("")
        self.var_co_borrower_name.set("")
        self.var_address_line1.set("")
        self.var_address_line2.set("")
        self.var_village_city.set("")
        self.var_taluka.set("")
        self.var_district.set("")
        self.var_pin_code.set("")
        self.var_mobile.set("")
        self.var_bank_name.set("")
        self.var_loan_amount.set("")
        self.var_letter_status.set("Not Send")
        self.notes_text.delete("1.0", tk.END)
        
        # Update form title
        self.form_title.config(text="Add New Borrower")

    def cancel_edit(self):
        """Cancel the current edit operation."""
        self.clear_form()
        self.tab_control.select(self.tab_list)

    def validate_form(self):
        """Validate the borrower form data."""
        # Check required fields
        if not self.var_borrower_name.get().strip():
            messagebox.showerror("Validation Error", "Borrower name is required.")
            return False
        
        if not self.var_address_line1.get().strip():
            messagebox.showerror("Validation Error", "Address Line 1 is required.")
            return False
        
        if not self.var_village_city.get().strip():
            messagebox.showerror("Validation Error", "Village/City is required.")
            return False
        
        if not self.var_district.get().strip():
            messagebox.showerror("Validation Error", "District is required.")
            return False
        
        # Validate PIN code
        pin_code = self.var_pin_code.get().strip()
        if pin_code and (not pin_code.isdigit() or len(pin_code) != 6):
            messagebox.showerror("Validation Error", "PIN code must be a 6-digit number.")
            return False
        
        # Validate mobile number
        mobile = self.var_mobile.get().strip()
        if mobile and (not mobile.isdigit() or len(mobile) != 10):
            messagebox.showerror("Validation Error", "Mobile number must be a 10-digit number.")
            return False
        
        # Validate loan amount
        loan_amount = self.var_loan_amount.get().strip()
        if loan_amount:
            try:
                float(loan_amount)
            except ValueError:
                messagebox.showerror("Validation Error", "Loan amount must be a number.")
                return False
        
        return True

    def save_borrower(self):
        """Save borrower data (add new or update existing)."""
        if not self.validate_form():
            return
        
        # Get form data
        borrower_data = {
            "date": self.var_date.get(),
            "reference": self.var_reference.get(),
            "borrower_name": self.var_borrower_name.get(),
            "co_borrower_name": self.var_co_borrower_name.get(),
            "address_line1": self.var_address_line1.get(),
            "address_line2": self.var_address_line2.get(),
            "village_city": self.var_village_city.get(),
            "taluka": self.var_taluka.get(),
            "district": self.var_district.get(),
            "pin_code": self.var_pin_code.get(),
            "mobile": self.var_mobile.get(),
            "bank_name": self.var_bank_name.get(),
            "loan_amount": self.var_loan_amount.get(),
            "letter_status": self.var_letter_status.get(),
            "notes": self.notes_text.get("1.0", tk.END).strip()
        }
        
        try:
            if self.current_borrower_id:
                # Update existing borrower
                update_borrower(self.current_borrower_id, borrower_data)
                messagebox.showinfo("Success", "Borrower information updated successfully.")
            else:
                # Add new borrower
                add_borrower(borrower_data)
                messagebox.showinfo("Success", "New borrower added successfully.")
            
            # Refresh data
            self.load_borrowers()
            self.load_dropdown_options()
            self.load_docs_borrowers()
            self.load_search_dropdowns()
            
            # Clear form and switch to list tab
            self.clear_form()
            self.tab_control.select(self.tab_list)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save borrower: {str(e)}")

    def confirm_delete(self):
        """Confirm borrower deletion."""
        if not self.current_borrower_id:
            messagebox.showinfo("Select a Borrower", "Please select a borrower to delete.")
            return
        
        # Get borrower name
        borrower = get_borrower_by_id(self.current_borrower_id)
        if not borrower:
            messagebox.showerror("Error", "Failed to load borrower data.")
            return
        
        # Confirm deletion
        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete borrower: {borrower['borrower_name']}?"
        )
        
        if confirmed:
            self.delete_selected_borrower()

    def delete_selected_borrower(self):
        """Delete the selected borrower."""
        if not self.current_borrower_id:
            return
        
        try:
            # Delete borrower
            delete_borrower(self.current_borrower_id)
            messagebox.showinfo("Success", "Borrower deleted successfully.")
            
            # Refresh data
            self.load_borrowers()
            self.load_dropdown_options()
            self.load_docs_borrowers()
            self.load_search_dropdowns()
            
            # Clear current selection
            self.current_borrower_id = None
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete borrower: {str(e)}")

    def view_documents(self):
        """View documents for the selected borrower."""
        if not self.current_borrower_id:
            messagebox.showinfo("Select a Borrower", "Please select a borrower to view documents.")
            return
        
        # Switch to documents tab
        self.tab_control.select(self.tab_docs)
        
        # Get borrower name
        borrower = get_borrower_by_id(self.current_borrower_id)
        if not borrower:
            messagebox.showerror("Error", "Failed to load borrower data.")
            return
        
        # Find and select the borrower in the documents tab list
        for i in range(self.docs_borrowers_listbox.size()):
            item_text = self.docs_borrowers_listbox.get(i)
            if str(borrower["serial_no"]) in item_text:
                self.docs_borrowers_listbox.selection_clear(0, tk.END)
                self.docs_borrowers_listbox.selection_set(i)
                self.docs_borrowers_listbox.see(i)
                # Trigger selection event
                self.load_documents_for_borrower(self.current_borrower_id)
                break

    def load_documents_for_borrower(self, borrower_id):
        """Load documents for the selected borrower in the documents tab."""
        # Clear existing items
        for item in self.docs_tree.get_children():
            self.docs_tree.delete(item)
        
        # Get documents
        documents = get_documents_for_borrower(borrower_id)
        
        # Add to treeview
        for doc in documents:
            values = (
                doc["id"],
                doc["filename"],
                doc["upload_date"],
                doc["description"]
            )
            self.docs_tree.insert("", "end", values=values)

    def upload_new_document(self):
        """Upload a new document for the selected borrower."""
        # Check if a borrower is selected in the documents tab
        selected_idx = self.docs_borrowers_listbox.curselection()
        if not selected_idx:
            messagebox.showinfo("Select a Borrower", "Please select a borrower to upload a document for.")
            return
        
        # Get the borrower_id from the selected item
        borrower_id = self.docs_borrowers_listbox.itemcget(selected_idx[0], "borrower_id")
        
        # Open file dialog to select document
        file_path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=(
                ("PDF files", "*.pdf"),
                ("Word files", "*.docx;*.doc"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            )
        )
        
        if not file_path:
            return  # User cancelled
        
        # Get document description
        description = simpledialog.askstring(
            "Document Description",
            "Enter a description for this document:",
            parent=self.root
        )
        
        if description is None:
            return  # User cancelled
        
        try:
            # Upload document
            upload_document(borrower_id, file_path, description)
            messagebox.showinfo("Success", "Document uploaded successfully.")
            
            # Refresh document list
            self.load_documents_for_borrower(borrower_id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload document: {str(e)}")

    def view_document(self):
        """View the selected document."""
        selected_items = self.docs_tree.selection()
        if not selected_items:
            messagebox.showinfo("Select a Document", "Please select a document to view.")
            return
        
        # Get document ID
        doc_id = self.docs_tree.item(selected_items[0], "values")[0]
        
        # Open document
        self.open_document_by_id(doc_id)

    def open_document(self, event):
        """Handle double-click on document in the tree."""
        item = self.docs_tree.identify("item", event.x, event.y)
        if item:
            # Get document ID
            doc_id = self.docs_tree.item(item, "values")[0]
            
            # Open document
            self.open_document_by_id(doc_id)

    def open_document_by_id(self, doc_id):
        """Open a document by its ID."""
        try:
            # Get document path
            doc_path = self.get_document_path(doc_id)
            
            # Open document with default application
            if os.path.exists(doc_path):
                import subprocess
                import platform
                
                if platform.system() == 'Windows':
                    os.startfile(doc_path)
                elif platform.system() == 'Linux':
                    subprocess.call(['xdg-open', doc_path])
                else:  # macOS
                    subprocess.call(['open', doc_path])
            else:
                messagebox.showinfo("File Not Found", "The document file could not be found.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open document: {str(e)}")

    def get_document_path(self, doc_id):
        """Get the file path of a document by its ID."""
        # This is a placeholder - actual implementation would retrieve from database
        # This should be implemented in document_handler.py
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM documents WHERE id = ?", (doc_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            raise ValueError(f"Document with ID {doc_id} not found")

    def delete_document(self):
        """Delete the selected document."""
        selected_items = self.docs_tree.selection()
        if not selected_items:
            messagebox.showinfo("Select a Document", "Please select a document to delete.")
            return
        
        # Get document ID and name
        doc_values = self.docs_tree.item(selected_items[0], "values")
        doc_id = doc_values[0]
        doc_name = doc_values[1]
        
        # Confirm deletion
        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete document: {doc_name}?"
        )
        
        if confirmed:
            try:
                # Get the borrower_id from currently selected borrower
                selected_idx = self.docs_borrowers_listbox.curselection()
                if selected_idx:
                    borrower_id = self.docs_borrowers_listbox.itemcget(selected_idx[0], "borrower_id")
                    
                    # Delete document (implement this in document_handler.py)
                    # delete_document(doc_id)
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Get file path before deleting
                    cursor.execute("SELECT file_path FROM documents WHERE id = ?", (doc_id,))
                    result = cursor.fetchone()
                    
                    if result and result[0] and os.path.exists(result[0]):
                        # Delete the file
                        os.remove(result[0])
                    
                    # Delete from database
                    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
                    conn.commit()
                    conn.close()
                    
                    messagebox.showinfo("Success", "Document deleted successfully.")
                    
                    # Refresh document list
                    self.load_documents_for_borrower(borrower_id)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete document: {str(e)}")

    def perform_search(self):
        """Perform search based on criteria."""
        # Get search criteria
        search_criteria = {
            "village_city": self.search_var_village.get(),
            "taluka": self.search_var_taluka.get(),
            "district": self.search_var_district.get(),
            "bank_name": self.search_var_bank.get(),
            "borrower_name": self.search_var_name.get(),
            "reference": self.search_var_reference.get()
        }
        
        # Remove empty criteria
        search_criteria = {k: v for k, v in search_criteria.items() if v}
        
        if not search_criteria:
            messagebox.showinfo("Search Criteria", "Please enter at least one search criterion.")
            return
        
        # Perform search
        self.search_results = search_borrowers(search_criteria)
        
        # Clear existing items
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # Add to treeview
        for i, borrower in enumerate(self.search_results):
            values = (
                borrower["serial_no"],
                borrower["date"],
                borrower["reference"],
                borrower["borrower_name"],
                borrower["co_borrower_name"],
                borrower["village_city"],
                borrower["taluka"],
                borrower["district"],
                borrower["bank_name"],
                borrower["loan_amount"],
                borrower["letter_status"]
            )
            self.search_tree.insert("", "end", iid=str(i), values=values)

    def clear_search(self):
        """Clear search criteria and results."""
        self.search_var_village.set("")
        self.search_var_taluka.set("")
        self.search_var_district.set("")
        self.search_var_bank.set("")
        self.search_var_name.set("")
        self.search_var_reference.set("")
        
        # Clear search results
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        self.search_results = []

    def view_selected_borrower(self):
        """View details of a borrower selected in search results."""
        selected_items = self.search_tree.selection()
        if not selected_items:
            messagebox.showinfo("Select a Borrower", "Please select a borrower to view.")
            return
        
        # Get selected borrower index
        selected_idx = int(selected_items[0])
        
        if 0 <= selected_idx < len(self.search_results):
            # Set current borrower
            self.current_borrower_id = self.search_results[selected_idx]["id"]
            
            # Edit borrower (loads the form)
            self.edit_borrower()

    def export_search_results(self):
        """Export search results to Excel file."""
        if not self.search_results:
            messagebox.showinfo("No Results", "There are no search results to export.")
            return
        
        # Open file dialog
        file_path = filedialog.asksaveasfilename(
            title="Export Search Results",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Export to Excel
            export_to_excel(self.search_results, file_path)
            messagebox.showinfo("Success", f"Search results exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export search results: {str(e)}")

    def export_data(self):
        """Export all borrowers to Excel file."""
        # Open file dialog
        file_path = filedialog.asksaveasfilename(
            title="Export Borrowers",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Get all borrowers
            borrowers = get_all_borrowers()
            
            # Export to Excel
            export_to_excel(borrowers, file_path)
            messagebox.showinfo("Success", f"Borrowers exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export borrowers: {str(e)}")

    def import_data(self):
        """Import borrowers from Excel file."""
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Import Borrowers",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Confirm import
            confirmed = messagebox.askyesno(
                "Confirm Import",
                "Importing may add duplicate records. Continue?"
            )
            
            if not confirmed:
                return
            
            # Import from Excel
            count = import_from_excel(file_path)
            messagebox.showinfo("Success", f"{count} borrowers imported successfully.")
            
            # Refresh data
            self.load_borrowers()
            self.load_dropdown_options()
            self.load_docs_borrowers()
            self.load_search_dropdowns()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import borrowers: {str(e)}")

    def pick_date(self, date_var):
        """Show date picker and set value to the given variable."""
        def set_date(date):
            date_var.set(date)
            date_dialog.destroy()
        
        date_dialog = tk.Toplevel(self.root)
        date_dialog.title("Select Date")
        date_dialog.geometry("300x250")
        date_dialog.transient(self.root)  # Set to be on top of the main window
        date_dialog.grab_set()  # Modal
        
        cal = Calendar(date_dialog, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Button(date_dialog, text="Select", command=lambda: set_date(cal.get_date())).pack(pady=5)

    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About",
            "Maharashtra Lokadhikar Samiti - Borrower Management System\n\n"
            "Version 1.0\n\n"
            "A desktop application for managing borrower information, "
            "debt correspondence, and loan documents."
        )


if __name__ == "__main__":
    # Create root window
    root = tk.Tk()
    app = BorrowerManagementApp(root)
    root.mainloop()
