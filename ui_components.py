"""
UI Components for the Borrower Management System.
Custom widgets and components for use in the tkinter interface.
"""
import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime

class Calendar(ttk.Frame):
    """A simple calendar widget for date selection."""
    
    def __init__(self, parent, selectmode='day', date_pattern='yyyy-mm-dd'):
        """
        Initialize the calendar widget.
        
        Args:
            parent: The parent widget
            selectmode (str): Selection mode, 'day' or 'month'
            date_pattern (str): Date format pattern
        """
        super().__init__(parent)
        
        self.parent = parent
        self.selectmode = selectmode
        self.date_pattern = date_pattern
        
        # Initialize date to today
        self.today = datetime.now()
        self.current_year = self.today.year
        self.current_month = self.today.month
        
        # Create calendar UI
        self.setup_ui()
        
        # Display the calendar
        self.fill_calendar()
    
    def setup_ui(self):
        """Setup the calendar UI components."""
        # Header frame
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(fill='x', padx=5, pady=5)
        
        # Previous button
        self.prev_button = ttk.Button(
            self.header_frame, text='<', width=3,
            command=self.prev_month
        )
        self.prev_button.pack(side='left')
        
        # Month/Year label
        self.month_year_var = tk.StringVar()
        self.month_year_label = ttk.Label(
            self.header_frame, textvariable=self.month_year_var,
            width=15, anchor='center'
        )
        self.month_year_label.pack(side='left', padx=5)
        
        # Next button
        self.next_button = ttk.Button(
            self.header_frame, text='>', width=3,
            command=self.next_month
        )
        self.next_button.pack(side='left')
        
        # Calendar frame
        self.cal_frame = ttk.Frame(self)
        self.cal_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Days of week
        self.dow_labels = []
        for i, day in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']):
            label = ttk.Label(self.cal_frame, text=day, width=4, anchor='center')
            label.grid(row=0, column=i, padx=1, pady=1)
            self.dow_labels.append(label)
        
        # Calendar days
        self.day_buttons = []
        for row in range(6):
            for col in range(7):
                btn = ttk.Button(
                    self.cal_frame, text='', width=4,
                    command=lambda r=row, c=col: self.select_day(r, c)
                )
                btn.grid(row=row+1, column=col, padx=1, pady=1)
                self.day_buttons.append(btn)
    
    def fill_calendar(self):
        """Fill the calendar with days for the current month/year."""
        # Update month/year label
        month_name = calendar.month_name[self.current_month]
        self.month_year_var.set(f"{month_name} {self.current_year}")
        
        # Clear all day buttons
        for btn in self.day_buttons:
            btn.config(text='')
            btn.state(['!pressed'])
        
        # Get first day of the month (0 = Monday, 6 = Sunday)
        first_day = datetime(self.current_year, self.current_month, 1).weekday()
        
        # Get number of days in month
        month_days = calendar.monthrange(self.current_year, self.current_month)[1]
        
        # Fill calendar
        for i in range(month_days):
            day = i + 1
            btn_idx = first_day + i
            if btn_idx < len(self.day_buttons):
                self.day_buttons[btn_idx].config(text=str(day))
    
    def prev_month(self):
        """Move to the previous month."""
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.fill_calendar()
    
    def next_month(self):
        """Move to the next month."""
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.fill_calendar()
    
    def select_day(self, row, col):
        """
        Handle day selection.
        
        Args:
            row (int): Button row
            col (int): Button column
        """
        btn_idx = row * 7 + col
        if btn_idx < len(self.day_buttons):
            btn = self.day_buttons[btn_idx]
            day_text = btn.cget('text')
            
            if day_text:
                self.selected_date = datetime(
                    self.current_year, self.current_month, int(day_text)
                )
    
    def get_date(self):
        """
        Get the selected date.
        
        Returns:
            str: Selected date in the format specified by date_pattern
        """
        selected_date = getattr(self, 'selected_date', self.today)
        
        if self.date_pattern == 'yyyy-mm-dd':
            return selected_date.strftime('%Y-%m-%d')
        elif self.date_pattern == 'dd-mm-yyyy':
            return selected_date.strftime('%d-%m-%Y')
        else:
            return selected_date.strftime('%Y-%m-%d')

class ValidatingEntry(ttk.Entry):
    """An entry widget that validates input."""
    
    def __init__(self, parent, validate_func=None, **kwargs):
        """
        Initialize the validating entry.
        
        Args:
            parent: The parent widget
            validate_func (callable): Function to validate input
            **kwargs: Additional arguments for ttk.Entry
        """
        # Register validation function
        vcmd = (parent.register(self.validate), '%P')
        
        super().__init__(
            parent, validate='key', validatecommand=vcmd, **kwargs
        )
        
        self.validate_func = validate_func
    
    def validate(self, new_value):
        """
        Validate input.
        
        Args:
            new_value (str): New value to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if self.validate_func:
            return self.validate_func(new_value)
        return True

class ScrollableFrame(ttk.Frame):
    """A scrollable frame that can contain arbitrary widgets."""
    
    def __init__(self, parent, **kwargs):
        """
        Initialize the scrollable frame.
        
        Args:
            parent: The parent widget
            **kwargs: Additional arguments for ttk.Frame
        """
        super().__init__(parent, **kwargs)
        
        # Create a canvas widget
        self.canvas = tk.Canvas(self)
        
        # Add a scrollbar
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        
        # Create the scrollable frame
        self.scrolled_frame = ttk.Frame(self.canvas)
        
        # Configure the canvas to scroll the frame
        self.scrolled_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        # Create a window inside the canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrolled_frame, anchor="nw"
        )
        
        # Configure the canvas to resize with the window
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        
        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack the scrollbar and canvas
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mouse wheel scrolling
        self.bind_mousewheel()
    
    def on_canvas_resize(self, event):
        """
        Handle canvas resize event.
        
        Args:
            event: The resize event
        """
        # Update the width of the canvas window
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def bind_mousewheel(self):
        """Bind mouse wheel events to the canvas."""
        def on_mousewheel(event):
            # Scroll up or down according to the mousewheel direction
            if event.delta > 0:
                self.canvas.yview_scroll(-1, "units")
            else:
                self.canvas.yview_scroll(1, "units")
        
        # Bind mousewheel event
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
