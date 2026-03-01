# main.py
import tkinter as tk
from gui import DutySchedulerGUI

def main():
    root = tk.Tk()
    root.title("Duty Scheduler - Loading...")
    
    # Set window icon and position
    root.geometry("1200x700")
    root.minsize(1000, 600)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (1200 // 2)
    y = (root.winfo_screenheight() // 2) - (700 // 2)
    root.geometry(f"1200x700+{x}+{y}")
    
    app = DutySchedulerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()