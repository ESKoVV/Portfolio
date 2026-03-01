# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from database import Database
from scheduler import Scheduler
from config import Config
from styles import Styles

class AddPersonDialog:
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Person")
        self.dialog.geometry("400x400")
        self.dialog.configure(bg=Styles.COLORS["bg_secondary"])
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 200
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, style="Custom.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Add New Person", style="Header.TLabel")
        title_label.pack(fill=tk.X, pady=(0, 20))
        
        # Form frame
        form_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(form_frame, text="Full Name:", style="Custom.TLabel").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var, style="Custom.TEntry", width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=8, padx=10)
        name_entry.focus()
        
        # Duty Count
        ttk.Label(form_frame, text="Duty Count:", style="Custom.TLabel").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.duty_var = tk.StringVar(value="0")
        duty_entry = ttk.Entry(form_frame, textvariable=self.duty_var, style="Custom.TEntry", width=30)
        duty_entry.grid(row=1, column=1, sticky=tk.W, pady=8, padx=10)
        
        # VPI Count
        ttk.Label(form_frame, text="VPI Count:", style="Custom.TLabel").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.vpi_var = tk.StringVar(value="0")
        vpi_entry = ttk.Entry(form_frame, textvariable=self.vpi_var, style="Custom.TEntry", width=30)
        vpi_entry.grid(row=2, column=1, sticky=tk.W, pady=8, padx=10)
        
        # Guard Count
        ttk.Label(form_frame, text="Guard Count:", style="Custom.TLabel").grid(row=3, column=0, sticky=tk.W, pady=8)
        self.guard_var = tk.StringVar(value="0")
        guard_entry = ttk.Entry(form_frame, textvariable=self.guard_var, style="Custom.TEntry", width=30)
        guard_entry.grid(row=3, column=1, sticky=tk.W, pady=8, padx=10)
        
        # Status checkboxes
        self.is_senior_var = tk.BooleanVar()
        senior_check = ttk.Checkbutton(form_frame, text="Senior", variable=self.is_senior_var, 
                                      style="Custom.TLabel")
        senior_check.grid(row=4, column=0, sticky=tk.W, pady=8, padx=10)
        
        self.is_wounded_var = tk.BooleanVar()
        wounded_check = ttk.Checkbutton(form_frame, text="Wounded", variable=self.is_wounded_var,
                                       style="Custom.TLabel")
        wounded_check.grid(row=4, column=1, sticky=tk.W, pady=8, padx=10)
        
        self.is_commander_var = tk.BooleanVar()
        commander_check = ttk.Checkbutton(form_frame, text="Commander", variable=self.is_commander_var,
                                         style="Custom.TLabel")
        commander_check.grid(row=5, column=0, sticky=tk.W, pady=8, padx=10)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Add", command=self.add_person, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel, style="Secondary.TButton").pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key to add person
        self.dialog.bind('<Return>', lambda e: self.add_person())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def add_person(self):
        name = self.name_var.get().strip()
        duty_count = self.duty_var.get().strip()
        vpi_count = self.vpi_var.get().strip()
        guard_count = self.guard_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter a name", parent=self.dialog)
            return
        
        # Validate numbers
        try:
            duty_count = int(duty_count) if duty_count else 0
            vpi_count = int(vpi_count) if vpi_count else 0
            guard_count = int(guard_count) if guard_count else 0
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for counts", parent=self.dialog)
            return
        
        self.result = (name, duty_count, vpi_count, guard_count, 
                      int(self.is_senior_var.get()), 
                      int(self.is_wounded_var.get()), 
                      int(self.is_commander_var.get()))
        self.dialog.destroy()
    
    def cancel(self):
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        self.dialog.wait_window()
        return self.result

class ReplacePersonDialog:
    def __init__(self, parent, available_people, current_person):
        self.parent = parent
        self.available_people = available_people
        self.current_person = current_person
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Replace Person")
        self.dialog.geometry("400x200")
        self.dialog.configure(bg=Styles.COLORS["bg_secondary"])
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, style="Custom.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"Replace {self.current_person}", style="Header.TLabel")
        title_label.pack(fill=tk.X, pady=(0, 20))
        
        # Current person label
        current_label = ttk.Label(main_frame, text=f"Current: {self.current_person}", style="Custom.TLabel")
        current_label.pack(fill=tk.X, pady=5)
        
        # New person selection
        ttk.Label(main_frame, text="Select new person:", style="Custom.TLabel").pack(anchor=tk.W, pady=5)
        
        self.new_person_var = tk.StringVar()
        person_combo = ttk.Combobox(main_frame, textvariable=self.new_person_var, 
                                   values=self.available_people,
                                   style="Custom.TCombobox", state="readonly")
        person_combo.pack(fill=tk.X, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Replace", command=self.replace_person, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel, style="Secondary.TButton").pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key to replace person
        self.dialog.bind('<Return>', lambda e: self.replace_person())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def replace_person(self):
        new_person = self.new_person_var.get()
        if not new_person:
            messagebox.showerror("Error", "Please select a person", parent=self.dialog)
            return
        
        self.result = new_person
        self.dialog.destroy()
    
    def cancel(self):
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        self.dialog.wait_window()
        return self.result

class ScheduleCell:
    def __init__(self, parent, person_name, role, date, is_senior=False):
        self.parent = parent
        self.person_name = person_name
        self.role = role
        self.date = date
        self.is_senior = is_senior
        self.checked = False
        
        self.frame = ttk.Frame(parent, style="Custom.TFrame")
        self.name_label = ttk.Label(self.frame, text=person_name, style="Custom.TLabel")
        self.check_var = tk.BooleanVar(value=False)
        self.checkbox = ttk.Checkbutton(self.frame, variable=self.check_var, 
                                       command=self.on_checkbox_click)
        
        self.setup_appearance()
    
    def setup_appearance(self):
        # Configure frame
        if self.is_senior:
            self.frame.configure(style="Secondary.TFrame")
            self.name_label.configure(style="Header.TLabel")
        else:
            self.frame.configure(style="Custom.TFrame")
            self.name_label.configure(style="Custom.TLabel")
        
        # Pack widgets
        self.name_label.pack(side=tk.LEFT, padx=2, pady=1)
        self.checkbox.pack(side=tk.RIGHT, padx=2, pady=1)
        
        # Bind click events
        self.name_label.bind("<Button-1>", self.on_click)
        self.frame.bind("<Button-1>", self.on_click)
    
    def on_click(self, event):
        # Notify parent about cell selection
        if hasattr(self.parent, 'on_cell_select'):
            self.parent.on_cell_select(self)
    
    def on_checkbox_click(self):
        if self.check_var.get() and not self.checked:
            self.checked = True
            self.parent.on_checkbox_checked(self)
        elif not self.check_var.get() and self.checked:
            self.checked = False
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs, fill=tk.X, padx=1, pady=1)
    
    def grid(self, **kwargs):
        # Remove padx and pady from kwargs to avoid duplication
        grid_kwargs = kwargs.copy()
        if 'padx' in grid_kwargs:
            del grid_kwargs['padx']
        if 'pady' in grid_kwargs:
            del grid_kwargs['pady']
        self.frame.grid(**grid_kwargs, sticky="nsew", padx=1, pady=1)
    
    def destroy(self):
        self.frame.destroy()

class DutySchedulerGUI:
    def clear_all_counts(self):
        """Clear all duty, VPI and guard counts for all people"""
        result = messagebox.askyesno(
            "Clear All Counts", 
            "Are you sure you want to clear ALL duty, VPI and guard counts for ALL people? This action cannot be undone."
        )
    
        if result:
            # Get current people data
            people_data = []
            for item in self.people_tree.get_children():
                values = self.people_tree.item(item)["values"]
                name = values[1]
                # Set all counts to 0, keep statuses
                is_senior = values[5] == "✓"
                is_wounded = values[6] == "✓" 
                is_commander = values[7] == "✓"
                people_data.append((name, 0, 0, 0, is_senior, is_wounded, is_commander))
        
            # Save to database
            self.db.save_people(people_data)
        
            # Refresh display
            self.load_people()
            messagebox.showinfo("Success", "All counts cleared successfully!")
    def __init__(self, root):
        self.root = root
        self.root.title("Duty Scheduler - Russian Armed Forces")
        self.root.geometry("1200x700")
        
        # Configure styles first
        Styles.configure_styles()
        
        self.db = Database()
        self.scheduler = Scheduler(self.db)
        
        # Initialize schedule cells dictionary
        self.schedule_cells = {}
        
        self.setup_theme()
        self.create_widgets()
        self.load_data()
        
        # Store selected cell for replacement
        self.selected_cell = None
    
    def setup_theme(self):
        # Configure root window
        self.root.configure(bg=Styles.COLORS["bg_primary"])
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, style="Custom.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title with Russian flag colors
        title_frame = ttk.Frame(main_frame, style="Custom.TFrame")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title with Russian flag color stripes
        title_label = ttk.Label(title_frame, 
                               text="DUTY SCHEDULER - RUSSIAN ARMED FORCES", 
                               style="Header.TLabel")
        title_label.pack(fill=tk.X)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame, style="Custom.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # People tab
        people_frame = ttk.Frame(notebook, style="Custom.TFrame")
        notebook.add(people_frame, text="People Management")
        
        # Schedule tab
        schedule_frame = ttk.Frame(notebook, style="Custom.TFrame")
        notebook.add(schedule_frame, text="Schedule")
        
        # Settings tab
        settings_frame = ttk.Frame(notebook, style="Custom.TFrame")
        notebook.add(settings_frame, text="Settings")
        
        self.setup_people_tab(people_frame)
        self.setup_schedule_tab(schedule_frame)
        self.setup_settings_tab(settings_frame)
        
        # Status legend at the bottom
        self.create_status_legend(main_frame)
    
    def create_status_legend(self, parent):
        legend_frame = ttk.Frame(parent, style="Custom.TFrame")
        legend_frame.pack(fill=tk.X, pady=(10, 0))
        
        legend_text = "Color Legend:  Dark Green = Senior  |  Dark Gray = Wounded  |  Dark Red = Commander"
        legend_label = ttk.Label(legend_frame, text=legend_text, style="Instruction.TLabel")
        legend_label.pack(pady=5)
    
    def setup_people_tab(self, parent):
        # Instructions
        instructions = ttk.Label(parent, 
                               text="Add people with their current duty counts. Click buttons to change status. Click 'Save' to store data, then 'Generate Schedule' to create schedule.",
                               style="Custom.TLabel")
        instructions.pack(fill=tk.X, padx=5, pady=5)
    
        # People table frame
        table_frame = ttk.Frame(parent, style="Secondary.TFrame")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
        # Treeview for people
        columns = ("№", "Name", "Duty Count", "VPI Count", "Guard Count", "Senior", "Wounded", "Commander")
        self.people_tree = ttk.Treeview(table_frame, columns=columns, show="headings", 
                                       style="Custom.Treeview", height=15)
    
        # Configure columns
        self.people_tree.heading("№", text="№")
        self.people_tree.column("№", width=40)
    
        self.people_tree.heading("Name", text="Name")
        self.people_tree.column("Name", width=150)
    
        self.people_tree.heading("Duty Count", text="Duty Count")
        self.people_tree.column("Duty Count", width=80)
    
        self.people_tree.heading("VPI Count", text="VPI Count")
        self.people_tree.column("VPI Count", width=80)
    
        self.people_tree.heading("Guard Count", text="Guard Count")
        self.people_tree.column("Guard Count", width=80)
    
        self.people_tree.heading("Senior", text="Senior")
        self.people_tree.column("Senior", width=60)
    
        self.people_tree.heading("Wounded", text="Wounded")
        self.people_tree.column("Wounded", width=60)
    
        self.people_tree.heading("Commander", text="Commander")
        self.people_tree.column("Commander", width=80)
    
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, 
                                 command=self.people_tree.yview, style="Custom.Vertical.TScrollbar")
        self.people_tree.configure(yscrollcommand=scrollbar.set)
    
        self.people_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # Bind click event for status toggling
        self.people_tree.bind("<Button-1>", self.on_people_tree_click)
    
        # Buttons frame
        button_frame = ttk.Frame(parent, style="Custom.TFrame")
        button_frame.pack(fill=tk.X, padx=5, pady=5)
    
        ttk.Button(button_frame, text="Add Person", command=self.add_person, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Person", command=self.delete_person, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All Counts", command=self.clear_all_counts, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save", command=self.save_people, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate Schedule", command=self.generate_schedule, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
    def setup_schedule_tab(self, parent):
        # Instructions
        instructions = ttk.Label(parent, 
                               text="Generated schedule showing duties for each Monday. Select a cell and click 'Replace Person' to make adjustments. Click checkboxes to confirm presence.",
                               style="Custom.TLabel")
        instructions.pack(fill=tk.X, padx=5, pady=5)
        
        # Main schedule container
        main_schedule_frame = ttk.Frame(parent, style="Custom.TFrame")
        main_schedule_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a canvas with scrollbars for the schedule
        self.schedule_canvas = tk.Canvas(main_schedule_frame, bg=Styles.COLORS["bg_secondary"],
                                        highlightthickness=0)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(main_schedule_frame, orient=tk.VERTICAL, 
                                   command=self.schedule_canvas.yview, style="Custom.Vertical.TScrollbar")
        h_scrollbar = ttk.Scrollbar(main_schedule_frame, orient=tk.HORIZONTAL, 
                                   command=self.schedule_canvas.xview, style="Custom.Horizontal.TScrollbar")
        
        self.schedule_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Scrollable frame inside canvas
        self.schedule_frame = ttk.Frame(self.schedule_canvas, style="Custom.TFrame")
        self.schedule_window = self.schedule_canvas.create_window((0, 0), window=self.schedule_frame, anchor="nw")
        
        # Grid layout for scrollbars and canvas
        self.schedule_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        main_schedule_frame.grid_rowconfigure(0, weight=1)
        main_schedule_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events for scrolling and resizing
        self.schedule_frame.bind("<Configure>", self.on_schedule_frame_configure)
        self.schedule_canvas.bind("<Configure>", self.on_schedule_canvas_configure)
        
        # Buttons frame
        button_frame = ttk.Frame(parent, style="Custom.TFrame")
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Replace Person", command=self.replace_person, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh Schedule", command=self.refresh_schedule, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Schedule", command=self.clear_schedule, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
    
    def clear_schedule(self):
        """Clear the entire schedule"""
        result = messagebox.askyesno(
            "Clear Schedule", 
            "Are you sure you want to clear the entire schedule? This action cannot be undone."
        )
        
        if result:
            # Clear schedule from database
            self.db.save_schedule([])
            # Refresh the display
            self.load_schedule()
            messagebox.showinfo("Success", "Schedule cleared successfully!")
    
    def on_schedule_frame_configure(self, event):
        # Update scrollregion when frame size changes
        self.schedule_canvas.configure(scrollregion=self.schedule_canvas.bbox("all"))
    
    def on_schedule_canvas_configure(self, event):
        # Resize the inner frame to match canvas width
        self.schedule_canvas.itemconfig(self.schedule_window, width=event.width)
    
    def setup_settings_tab(self, parent):
        # Instructions
        instructions = ttk.Label(parent, 
                               text="Configure scheduling parameters. Changes take effect after generating new schedule.",
                               style="Custom.TLabel")
        instructions.pack(fill=tk.X, padx=5, pady=5)
        
        settings_frame = ttk.Frame(parent, style="Secondary.TFrame")
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Training day
        ttk.Label(settings_frame, text="Training Day:", style="Custom.TLabel").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.training_day_var = tk.StringVar(value=self.db.get_setting('training_day'))
        training_day_combo = ttk.Combobox(settings_frame, textvariable=self.training_day_var, 
                                         values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                         style="Custom.TCombobox", state="readonly")
        training_day_combo.grid(row=0, column=1, sticky=tk.W, pady=8, padx=10)
        
        # Duty per week
        ttk.Label(settings_frame, text="Duty Persons per Week:", style="Custom.TLabel").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.duty_per_week_var = tk.StringVar(value=self.db.get_setting('duty_per_week'))
        duty_entry = ttk.Entry(settings_frame, textvariable=self.duty_per_week_var, style="Custom.TEntry")
        duty_entry.grid(row=1, column=1, sticky=tk.W, pady=8, padx=10)
        
        # VPI per week
        ttk.Label(settings_frame, text="VPI Persons per Week:", style="Custom.TLabel").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.vpi_per_week_var = tk.StringVar(value=self.db.get_setting('vpi_per_week'))
        vpi_entry = ttk.Entry(settings_frame, textvariable=self.vpi_per_week_var, style="Custom.TEntry")
        vpi_entry.grid(row=2, column=1, sticky=tk.W, pady=8, padx=10)
        
        # Guard count
        ttk.Label(settings_frame, text="Guard Persons Count:", style="Custom.TLabel").grid(row=3, column=0, sticky=tk.W, pady=8)
        self.guard_count_var = tk.StringVar(value=self.db.get_setting('guard_count'))
        guard_entry = ttk.Entry(settings_frame, textvariable=self.guard_count_var, style="Custom.TEntry")
        guard_entry.grid(row=3, column=1, sticky=tk.W, pady=8, padx=10)
        
        # People count
        ttk.Label(settings_frame, text="Total People Count:", style="Custom.TLabel").grid(row=4, column=0, sticky=tk.W, pady=8)
        self.people_count_var = tk.StringVar(value=self.db.get_setting('people_count'))
        people_entry = ttk.Entry(settings_frame, textvariable=self.people_count_var, style="Custom.TEntry")
        people_entry.grid(row=4, column=1, sticky=tk.W, pady=8, padx=10)
        
        # Guard frequency (CHANGED from Duty frequency)
        ttk.Label(settings_frame, text="Guard Frequency (weeks):", style="Custom.TLabel").grid(row=5, column=0, sticky=tk.W, pady=8)
        self.guard_frequency_var = tk.StringVar(value=self.db.get_setting('guard_frequency'))  # CHANGED
        frequency_entry = ttk.Entry(settings_frame, textvariable=self.guard_frequency_var, style="Custom.TEntry")
        frequency_entry.grid(row=5, column=1, sticky=tk.W, pady=8, padx=10)
        
        # First duty date
        ttk.Label(settings_frame, text="First Duty Date (YYYY-MM-DD):", style="Custom.TLabel").grid(row=6, column=0, sticky=tk.W, pady=8)
        self.first_duty_date_var = tk.StringVar(value=self.db.get_setting('first_duty_date'))
        first_duty_entry = ttk.Entry(settings_frame, textvariable=self.first_duty_date_var, style="Custom.TEntry")
        first_duty_entry.grid(row=6, column=1, sticky=tk.W, pady=8, padx=10)
        
        # Start date
        ttk.Label(settings_frame, text="Start Date (YYYY-MM-DD):", style="Custom.TLabel").grid(row=7, column=0, sticky=tk.W, pady=8)
        self.start_date_var = tk.StringVar(value=self.db.get_setting('start_date'))
        start_entry = ttk.Entry(settings_frame, textvariable=self.start_date_var, style="Custom.TEntry")
        start_entry.grid(row=7, column=1, sticky=tk.W, pady=8, padx=10)
        
        # End date
        ttk.Label(settings_frame, text="End Date (YYYY-MM-DD):", style="Custom.TLabel").grid(row=8, column=0, sticky=tk.W, pady=8)
        self.end_date_var = tk.StringVar(value=self.db.get_setting('end_date'))
        end_entry = ttk.Entry(settings_frame, textvariable=self.end_date_var, style="Custom.TEntry")
        end_entry.grid(row=8, column=1, sticky=tk.W, pady=8, padx=10)
        
        # Save button
        ttk.Button(settings_frame, text="Save Settings", command=self.save_settings, 
                  style="Accent.TButton").grid(row=9, column=0, columnspan=2, pady=20)
    
    def save_settings(self):
        settings = {
            'training_day': self.training_day_var.get(),
            'duty_per_week': self.duty_per_week_var.get(),
            'vpi_per_week': self.vpi_per_week_var.get(),
            'guard_count': self.guard_count_var.get(),
            'people_count': self.people_count_var.get(),
            'guard_frequency': self.guard_frequency_var.get(),  # CHANGED
            'first_duty_date': self.first_duty_date_var.get(),
            'start_date': self.start_date_var.get(),
            'end_date': self.end_date_var.get()
        }
        
        self.db.save_settings(settings)
        messagebox.showinfo("Success", "Settings saved successfully!")

    
    def load_data(self):
        self.load_people()
        self.load_schedule()
    
    def load_people(self):
        # Clear existing data
        for item in self.people_tree.get_children():
            self.people_tree.delete(item)
        
        # Load people from database
        people = self.db.get_people()
        for i, person in enumerate(people, 1):
            name, duty_count, vpi_count, guard_count, is_senior, is_wounded, is_commander = person
            
            # Insert with status indicators
            item_id = self.people_tree.insert("", tk.END, values=(
                i, name, duty_count, vpi_count, guard_count,
                "✓" if is_senior else "",
                "✓" if is_wounded else "",
                "✓" if is_commander else ""
            ))
            
            # Set background color based on status
            if is_commander:
                self.people_tree.item(item_id, tags=("commander",))
            elif is_wounded:
                self.people_tree.item(item_id, tags=("wounded",))
            elif is_senior:
                self.people_tree.item(item_id, tags=("senior",))
        
        # Configure tag colors
        self.people_tree.tag_configure("senior", background=Styles.COLORS["status_senior"])
        self.people_tree.tag_configure("wounded", background=Styles.COLORS["status_wounded"])
        self.people_tree.tag_configure("commander", background=Styles.COLORS["status_commander"])
    
    def load_schedule(self):
        # Clear existing schedule cells
        if hasattr(self, 'schedule_cells'):
            for cell_key in list(self.schedule_cells.keys()):
                cell = self.schedule_cells[cell_key]
                cell.destroy()
                del self.schedule_cells[cell_key]
        
        # Clear the schedule frame
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()
        
        # Load schedule from database
        schedule = self.db.get_schedule()
        if not schedule:
            # Show message if no schedule
            no_schedule_label = ttk.Label(self.schedule_frame, 
                                        text="No schedule generated. Click 'Generate Schedule' in People Management tab.",
                                        style="Custom.TLabel")
            no_schedule_label.pack(pady=50)
            return
        
        # Get people data to check senior status
        people_data = self.db.get_people()
        seniors = [p[0] for p in people_data if p[4]]  # Get names of seniors
        
        # Create a grid container for the schedule
        grid_container = ttk.Frame(self.schedule_frame, style="Custom.TFrame")
        grid_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create header row
        dates = [s[0] for s in schedule]
        roles = ["Duty", "VPI"] + [f"Guard {i+1}" for i in range(int(self.db.get_setting('guard_count')))]
        
        # Create header labels using grid
        # Role header (smaller width)
        role_header = ttk.Label(grid_container, text="Role", width=8, style="Header.TLabel")
        role_header.grid(row=0, column=0, padx=1, pady=1, sticky="nsew")
        
        # Date headers
        for i, date in enumerate(dates, 1):
            short_date = date[5:]  # Show only month and day
            date_header = ttk.Label(grid_container, text=short_date, width=12, style="Header.TLabel")
            date_header.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")
        
        # Create schedule grid
        for row_idx, role in enumerate(roles, 1):
            # Role label
            role_label = ttk.Label(grid_container, text=role, width=8, style="Custom.TLabel")
            role_label.grid(row=row_idx, column=0, padx=1, pady=1, sticky="nsew")
            
            # Create cells for each date
            for col_idx, schedule_item in enumerate(schedule, 1):
                date = schedule_item[0]
                
                # Get person for this role and date
                if role == "Duty":
                    person = schedule_item[1] or ""
                elif role == "VPI":
                    person = schedule_item[2] or ""
                else:  # Guard
                    guard_idx = int(role.split(" ")[1]) - 1
                    guard_people = schedule_item[3]
                    if guard_idx < len(guard_people):
                        person = guard_people[guard_idx] or ""
                    else:
                        person = ""
                
                # Check if person is senior
                is_senior = person in seniors
                
                # Create cell
                if person:  # Only create cell if there's a person
                    cell = ScheduleCell(grid_container, person, role, date, is_senior)
                    cell.grid(row=row_idx, column=col_idx)
                    
                    # Store cell reference
                    cell_key = f"{role}_{date}"
                    self.schedule_cells[cell_key] = cell
                    
                    # Set callback for cell selection
                    cell.parent = self  # Set parent reference for callbacks
    
    def on_cell_select(self, cell):
        """Handle cell selection for replacement"""
        self.selected_cell = {
            "person": cell.person_name,
            "role": cell.role,
            "date": cell.date
        }
    
    def on_checkbox_checked(self, cell):
        """Handle checkbox click to increment counters"""
        person_name = cell.person_name
        role = cell.role
        
        # Increment appropriate counter
        if role == "Duty":
            self.db.increment_duty_count(person_name)
        elif role == "VPI":
            self.db.increment_vpi_count(person_name)
        elif role.startswith("Guard"):
            self.db.increment_guard_count(person_name)
        
        # Refresh people data to show updated counts
        self.load_people()
        
        messagebox.showinfo("Success", f"Counter updated for {person_name}")
    
    def refresh_schedule(self):
        """Refresh schedule display"""
        self.load_schedule()
    
    def on_people_tree_click(self, event):
        # Get clicked item and column
        item = self.people_tree.identify_row(event.y)
        column = self.people_tree.identify_column(event.x)
        
        if item and column in ["#6", "#7", "#8"]:  # Senior, Wounded, Commander columns
            values = self.people_tree.item(item)["values"]
            
            # Get the actual person data (skip the serial number)
            name = values[1]
            duty_count = values[2]
            vpi_count = values[3]
            guard_count = values[4]
            is_senior = values[5] == "✓"
            is_wounded = values[6] == "✓"
            is_commander = values[7] == "✓"
            
            # Toggle status based on column
            if column == "#6":  # Senior column
                is_senior = not is_senior
                # Ensure only one status is active at a time
                if is_senior:
                    is_wounded = False
                    is_commander = False
            elif column == "#7":  # Wounded column
                is_wounded = not is_wounded
                if is_wounded:
                    is_senior = False
                    is_commander = False
            elif column == "#8":  # Commander column
                is_commander = not is_commander
                if is_commander:
                    is_senior = False
                    is_wounded = False
            
            # Update the treeview
            self.people_tree.set(item, "Senior", "✓" if is_senior else "")
            self.people_tree.set(item, "Wounded", "✓" if is_wounded else "")
            self.people_tree.set(item, "Commander", "✓" if is_commander else "")
            
            # Update tags for background color
            self.people_tree.item(item, tags=())
            if is_commander:
                self.people_tree.item(item, tags=("commander",))
            elif is_wounded:
                self.people_tree.item(item, tags=("wounded",))
            elif is_senior:
                self.people_tree.item(item, tags=("senior",))
    
    def add_person(self):
        dialog = AddPersonDialog(self.root)
        result = dialog.show()
        
        if result:
            name, duty_count, vpi_count, guard_count, is_senior, is_wounded, is_commander = result
            
            # Get the next serial number
            next_number = len(self.people_tree.get_children()) + 1
            
            item_id = self.people_tree.insert("", tk.END, values=(
                next_number, name, duty_count, vpi_count, guard_count,
                "✓" if is_senior else "",
                "✓" if is_wounded else "",
                "✓" if is_commander else ""
            ))
            
            # Set background color based on status
            if is_commander:
                self.people_tree.item(item_id, tags=("commander",))
            elif is_wounded:
                self.people_tree.item(item_id, tags=("wounded",))
            elif is_senior:
                self.people_tree.item(item_id, tags=("senior",))
    
    def delete_person(self):
        selected = self.people_tree.selection()
        if selected:
            self.people_tree.delete(selected)
            # Re-number the remaining items
            self.renumber_people()
    
    def renumber_people(self):
        """Renumber people after deletion"""
        for i, item in enumerate(self.people_tree.get_children(), 1):
            self.people_tree.set(item, "№", i)
    
    def save_people(self):
        people_data = []
        for item in self.people_tree.get_children():
            values = self.people_tree.item(item)["values"]
            # Skip the serial number (first element)
            name = values[1]
            duty_count = values[2]
            vpi_count = values[3]
            guard_count = values[4]
            is_senior = values[5] == "✓"
            is_wounded = values[6] == "✓"
            is_commander = values[7] == "✓"
            
            people_data.append((name, duty_count, vpi_count, guard_count, is_senior, is_wounded, is_commander))
        
        self.db.save_people(people_data)
        messagebox.showinfo("Success", "People data saved successfully!")
    
    def generate_schedule(self):
        # Clear old schedule and generate new one
        schedule = self.scheduler.generate_schedule()
        self.db.save_schedule(schedule)
        self.load_schedule()
        messagebox.showinfo("Success", "Schedule generated successfully!")
    
    def save_settings(self):
        settings = {
            'training_day': self.training_day_var.get(),
            'duty_per_week': self.duty_per_week_var.get(),
            'vpi_per_week': self.vpi_per_week_var.get(),
            'guard_count': self.guard_count_var.get(),
            'people_count': self.people_count_var.get(),
            'guard_frequency': self.guard_frequency_var.get(),  # CHANGED
            'first_duty_date': self.first_duty_date_var.get(),
            'start_date': self.start_date_var.get(),
            'end_date': self.end_date_var.get()
        }
        
        self.db.save_settings(settings)
        messagebox.showinfo("Success", "Settings saved successfully!")
    
    def replace_person(self):
        if not self.selected_cell:
            messagebox.showwarning("Warning", "Please select a cell first by clicking on a person's name in the schedule")
            return
        
        date = self.selected_cell["date"]
        role = self.selected_cell["role"]
        current_person = self.selected_cell["person"]
        
        # Get all people assigned on this date
        schedule = self.db.get_schedule()
        assigned_people = []
        for sched_date, duty_person, vpi_person, guard_people in schedule:
            if sched_date == date:
                assigned_people.extend([duty_person, vpi_person])
                assigned_people.extend(guard_people)
                break
        
        # Get available people (not wounded, not commanders, and not already assigned)
        available_people = self.scheduler.get_available_people_for_date(date, assigned_people)
        
        if not available_people:
            messagebox.showwarning("Warning", "No available people for replacement")
            return
        
        # Show dialog to select replacement
        dialog = ReplacePersonDialog(self.root, available_people, current_person)
        new_person = dialog.show()
        
        if new_person:
            # Find the person to swap with (who currently has new_person's assignment)
            swap_with = None
            swap_role = None
            
            for sched_date, duty_person, vpi_person, guard_people in schedule:
                if sched_date == date:
                    if duty_person == new_person:
                        swap_with = duty_person
                        swap_role = "duty"
                    elif vpi_person == new_person:
                        swap_with = vpi_person
                        swap_role = "vpi"
                    elif new_person in guard_people:
                        swap_with = new_person
                        swap_role = "guard"
                    break
            
            if swap_with:
                # Perform the swap
                if role == "duty":
                    self.scheduler.swap_people(date, role, current_person, new_person)
                    self.scheduler.swap_people(date, swap_role, swap_with, current_person)
                elif role == "vpi":
                    self.scheduler.swap_people(date, role, current_person, new_person)
                    self.scheduler.swap_people(date, swap_role, swap_with, current_person)
                elif role == "guard":
                    self.scheduler.swap_people(date, role, current_person, new_person)
                    self.scheduler.swap_people(date, swap_role, swap_with, current_person)
                
                self.refresh_schedule()
                messagebox.showinfo("Success", "Persons swapped successfully!")
            else:
                # Simple replacement
                self.scheduler.swap_people(date, role, current_person, new_person)
                self.refresh_schedule()
                messagebox.showinfo("Success", "Person replaced successfully!")