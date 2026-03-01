# styles.py
# Styles for VS Code 2022-like theme
class Styles:
    # Color scheme similar to VS Code 2022
    COLORS = {
        # Dark theme colors
        "bg_primary": "#1e1e1e",
        "bg_secondary": "#252526",
        "bg_tertiary": "#2d2d30",
        "bg_quaternary": "#3e3e42",
        
        # Text colors
        "text_primary": "#000000",  # BLACK for most elements
        "text_secondary": "#000000",  # BLACK
        "text_tertiary": "#000000",  # BLACK
        "text_dark": "#000000",  # BLACK
        "text_white": "#ffffff",  # WHITE for text on blue backgrounds
        
        # Accent colors
        "accent_blue": "#007acc",
        "accent_blue_light": "#1177bb",
        "accent_red": "#f44747",
        "accent_green": "#4ec9b0",
        "accent_yellow": "#ffcc02",
        "accent_orange": "#ce9178",
        
        # Russian flag colors
        "russian_white": "#ffffff",
        "russian_blue": "#0033a0",
        "russian_red": "#d52b1e",
        
        # UI elements
        "border": "#3e3e42",
        "hover": "#2a2d2e",
        "selection": "#094771",
        "button_hover": "#2a2d2e",
        
        # Status colors
        "status_senior": "#006400",  # Dark green
        "status_wounded": "#696969",  # Dark gray
        "status_commander": "#8B0000",  # Dark red
    }
    
    # Font settings
    FONTS = {
        "primary": ("Segoe UI", 10),
        "heading": ("Segoe UI", 12, "bold"),
        "title": ("Segoe UI", 16, "bold"),
        "monospace": ("Consolas", 10)
    }
    
    @classmethod
    def configure_styles(cls):
        import tkinter as tk
        from tkinter import ttk
        
        style = ttk.Style()
        
        # Configure main styles
        style.configure(".",
            background=cls.COLORS["bg_primary"],
            foreground=cls.COLORS["text_primary"],
            fieldbackground=cls.COLORS["bg_tertiary"],
            selectbackground=cls.COLORS["selection"],
            selectforeground=cls.COLORS["text_primary"],
            borderwidth=1,
            focuscolor="none"
        )
        
        # Frame styles
        style.configure("Custom.TFrame",
            background=cls.COLORS["bg_secondary"]
        )
        
        style.configure("Secondary.TFrame",
            background=cls.COLORS["bg_tertiary"]
        )
        
        # Label styles
        style.configure("Custom.TLabel",
            background=cls.COLORS["bg_secondary"],
            foreground=cls.COLORS["text_white"],
            font=cls.FONTS["primary"]
        )
        
        style.configure("Header.TLabel",
            background=cls.COLORS["russian_blue"],
            foreground=cls.COLORS["text_primary"],
            font=cls.FONTS["heading"],
            padding=(10, 5)
        )
        
        style.configure("Title.TLabel",
            background=cls.COLORS["bg_primary"],
            foreground=cls.COLORS["text_primary"],
            font=cls.FONTS["title"]
        )
        
        # Button styles
        style.configure("Accent.TButton",
            background=cls.COLORS["accent_blue"],
            foreground=cls.COLORS["text_primary"],
            font=cls.FONTS["primary"],
            borderwidth=0,
            focuscolor=cls.COLORS["accent_blue_light"],
            padding=(15, 5)
        )
        
        style.map("Accent.TButton",
            background=[("active", cls.COLORS["accent_blue_light"]),
                       ("pressed", cls.COLORS["accent_blue_light"])],
            foreground=[("active", cls.COLORS["text_primary"]),
                       ("pressed", cls.COLORS["text_primary"])]
        )
        
        style.configure("Secondary.TButton",
            background=cls.COLORS["bg_tertiary"],
            foreground=cls.COLORS["text_primary"],
            font=cls.FONTS["primary"],
            borderwidth=1,
            relief="raised",
            padding=(10, 4)
        )
        
        style.map("Secondary.TButton",
            background=[("active", cls.COLORS["bg_quaternary"]),
                       ("pressed", cls.COLORS["bg_quaternary"])],
            foreground=[("active", cls.COLORS["text_primary"]),
                       ("pressed", cls.COLORS["text_primary"])]
        )
        
        # Entry styles
        style.configure("Custom.TEntry",
            fieldbackground=cls.COLORS["bg_tertiary"],
            foreground=cls.COLORS["text_primary"],
            borderwidth=1,
            relief="sunken",
            padding=(5, 2)
        )
        
        style.map("Custom.TEntry",
            fieldbackground=[("focus", cls.COLORS["bg_tertiary"]),
                           ("readonly", cls.COLORS["bg_quaternary"])],
            foreground=[("focus", cls.COLORS["text_primary"]),
                       ("readonly", cls.COLORS["text_secondary"])]
        )
        
        # Combobox styles
        style.configure("Custom.TCombobox",
            fieldbackground=cls.COLORS["bg_tertiary"],
            foreground=cls.COLORS["text_primary"],
            background=cls.COLORS["bg_tertiary"],
            borderwidth=1,
            relief="sunken",
            padding=(5, 2)
        )
        
        style.map("Custom.TCombobox",
            fieldbackground=[("focus", cls.COLORS["bg_tertiary"]),
                           ("readonly", cls.COLORS["bg_quaternary"])],
            foreground=[("focus", cls.COLORS["text_primary"]),
                       ("readonly", cls.COLORS["text_secondary"])],
            background=[("active", cls.COLORS["bg_quaternary"])]
        )
        
        # Notebook styles
        style.configure("Custom.TNotebook",
            background=cls.COLORS["bg_secondary"],
            borderwidth=0
        )
        
        style.configure("Custom.TNotebook.Tab",
            background=cls.COLORS["bg_tertiary"],
            foreground=cls.COLORS["text_primary"],
            padding=(15, 5),
            borderwidth=1
        )
        
        style.map("Custom.TNotebook.Tab",
            background=[("selected", cls.COLORS["accent_blue"]),
                       ("active", cls.COLORS["bg_quaternary"])],
            foreground=[("selected", cls.COLORS["text_primary"]),
                       ("active", cls.COLORS["text_primary"])]
        )
        
        # Treeview styles
        style.configure("Custom.Treeview",
            background=cls.COLORS["bg_tertiary"],
            foreground=cls.COLORS["text_white"],
            fieldbackground=cls.COLORS["bg_tertiary"],
            borderwidth=0,
            relief="flat",
            rowheight=25
        )
        
        style.configure("Custom.Treeview.Heading",
            background=cls.COLORS["russian_blue"],
            foreground=cls.COLORS["text_primary"],
            relief="flat",
            borderwidth=0,
            font=cls.FONTS["heading"]
        )
        
        style.map("Custom.Treeview",
            background=[("selected", cls.COLORS["selection"])],
            foreground=[("selected", cls.COLORS["text_white"])]
        )
        
        # Scrollbar styles
        style.configure("Custom.Vertical.TScrollbar",
            background=cls.COLORS["bg_tertiary"],
            troughcolor=cls.COLORS["bg_secondary"],
            borderwidth=0,
            relief="flat",
            arrowsize=12
        )
        
        style.configure("Custom.Horizontal.TScrollbar",
            background=cls.COLORS["bg_tertiary"],
            troughcolor=cls.COLORS["bg_secondary"],
            borderwidth=0,
            relief="flat",
            arrowsize=12
        )
        
        style.map("Custom.Vertical.TScrollbar",
            background=[("active", cls.COLORS["bg_quaternary"]),
                       ("pressed", cls.COLORS["accent_blue"])]
        )
        
        style.map("Custom.Horizontal.TScrollbar",
            background=[("active", cls.COLORS["bg_quaternary"]),
                       ("pressed", cls.COLORS["accent_blue"])]
        )
        
        # Labelframe styles
        style.configure("Custom.TLabelframe",
            background=cls.COLORS["bg_secondary"],
            foreground=cls.COLORS["text_white"],
            borderwidth=1
        )
        
        style.configure("Custom.TLabelframe.Label",
            background=cls.COLORS["bg_secondary"],
            foreground=cls.COLORS["text_white"]
        )
        
        # Instruction label style
        style.configure("Instruction.TLabel",
            background=cls.COLORS["bg_secondary"],
            foreground=cls.COLORS["text_primary"],
            font=cls.FONTS["primary"],
            wraplength=800
        )