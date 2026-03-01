import sqlite3
import os
from datetime import datetime


class TaskDatabase:
    def __init__(self, db_name="tasks.db"):
        self.db_name = db_name
        self.init_database()
        
    def get_connection(self):
        return sqlite3.connect(self.db_name)
        
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                description TEXT DEFAULT '',
                task_type TEXT DEFAULT 'single',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subtasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                text TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                position INTEGER DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                parent_id INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                folder_id INTEGER,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
                FOREIGN KEY (folder_id) REFERENCES folders (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                date TEXT,
                completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
                UNIQUE(task_id, date)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS completed_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                task_text TEXT,
                task_description TEXT,
                task_type TEXT,
                completed_date TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_task(self, text, description="", task_type="single"):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (text, description, task_type) VALUES (?, ?, ?)", 
                      (text, description, task_type))
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id
        
    def update_task(self, task_id, new_text, new_description=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET text = ?, description = ? WHERE id = ?", 
                      (new_text, new_description, task_id))
        conn.commit()
        conn.close()
        
    def delete_task(self, task_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        
    def add_subtask(self, task_id, text):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subtasks (task_id, text) VALUES (?, ?)", (task_id, text))
        subtask_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return subtask_id
        
    def update_subtask(self, subtask_id, completed):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE subtasks SET completed = ? WHERE id = ?", (completed, subtask_id))
        conn.commit()
        conn.close()
        
    def delete_subtask(self, subtask_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
        conn.commit()
        conn.close()
        
    def get_subtasks(self, task_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, text, completed FROM subtasks WHERE task_id = ? ORDER BY position, id", (task_id,))
        subtasks = cursor.fetchall()
        conn.close()
        return subtasks
        
    def restore_task_from_completed(self, task_id, task_text, task_description, task_type):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (id, text, description, task_type) VALUES (?, ?, ?, ?)", 
                      (task_id, task_text, task_description, task_type))
        cursor.execute("DELETE FROM completed_tasks WHERE task_id = ?", (task_id,))
        conn.commit()
        conn.close()
        return task_id
        
    def get_all_tasks(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, text, description, task_type FROM tasks ORDER BY created_at DESC")
        tasks = cursor.fetchall()
        conn.close()
        return tasks
        
    def add_folder(self, name, parent_id=0):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO folders (name, parent_id) VALUES (?, ?)", (name, parent_id))
        folder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return folder_id
        
    def delete_folder(self, folder_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # First delete all subfolders recursively
            subfolders = self.get_subfolders(folder_id)
            for subfolder_id, _, _ in subfolders:
                self.delete_folder(subfolder_id)
            
            # Then delete the folder itself
            cursor.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
            conn.commit()
        except Exception as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()
        
    def update_folder_description(self, folder_id, description):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE folders SET description = ? WHERE id = ?", (description, folder_id))
        conn.commit()
        conn.close()
        
    def get_folder_description(self, folder_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT description FROM folders WHERE id = ?", (folder_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else ""
        
    def get_all_folders(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, parent_id FROM folders ORDER BY parent_id, name")
        folders = cursor.fetchall()
        conn.close()
        return folders
        
    def get_subfolders(self, parent_id=0):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, parent_id FROM folders WHERE parent_id = ? ORDER BY name", (parent_id,))
        folders = cursor.fetchall()
        conn.close()
        return folders
        
    def save_folder_tasks(self, folder_id, task_ids):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # First remove all tasks from this folder
            cursor.execute("DELETE FROM task_folders WHERE folder_id = ?", (folder_id,))
            
            # Then add the new tasks
            for task_id in task_ids:
                cursor.execute("INSERT INTO task_folders (task_id, folder_id) VALUES (?, ?)", 
                              (task_id, folder_id))
            conn.commit()
        except Exception as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()
        
    def remove_task_from_folder(self, task_id, folder_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM task_folders WHERE task_id = ? AND folder_id = ?", 
                      (task_id, folder_id))
        conn.commit()
        conn.close()
        
    def get_tasks_in_folder(self, folder_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.id, t.text, t.description, t.task_type
            FROM tasks t
            JOIN task_folders tf ON t.id = tf.task_id
            WHERE tf.folder_id = ?
        ''', (folder_id,))
        tasks = cursor.fetchall()
        conn.close()
        return tasks
        
    def add_task_to_calendar(self, task_id, date):
        """Add single task to calendar immediately"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Use INSERT OR REPLACE to handle duplicates
            cursor.execute("INSERT OR REPLACE INTO calendar_tasks (task_id, date, completed) VALUES (?, ?, 0)", 
                          (task_id, date))
            conn.commit()
        except Exception as e:
            print(f"Database error in add_task_to_calendar: {e}")
            raise e
        finally:
            conn.close()
    
    def remove_task_from_date(self, task_id, date):
        """Remove single task from date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM calendar_tasks WHERE task_id = ? AND date = ?", 
                      (task_id, date))
        conn.commit()
        conn.close()
    
    def save_date_tasks(self, date, task_ids):
        """Save all tasks for a date (replaces existing)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Remove existing tasks for this date
            cursor.execute("DELETE FROM calendar_tasks WHERE date = ?", (date,))
            # Add new tasks
            for task_id in task_ids:
                cursor.execute("INSERT INTO calendar_tasks (task_id, date, completed) VALUES (?, ?, 0)", 
                              (task_id, date))
            conn.commit()
        except Exception as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()
        
    def get_tasks_by_date(self, date):
        """Get tasks for specific date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.id, t.text, t.description, t.task_type, ct.completed
            FROM tasks t
            JOIN calendar_tasks ct ON t.id = ct.task_id
            WHERE ct.date = ?
            ORDER BY ct.completed, t.id
        ''', (date,))
        tasks = cursor.fetchall()
        conn.close()
        return tasks
    
    def get_dates_with_tasks(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT date FROM calendar_tasks
        ''')
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()
        return dates
    
    def mark_task_completed(self, task_id, date):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE calendar_tasks SET completed = 1 WHERE task_id = ? AND date = ?", 
                          (task_id, date))
            
            cursor.execute("SELECT text, description, task_type FROM tasks WHERE id = ?", (task_id,))
            task_data = cursor.fetchone()
            if task_data:
                task_text, task_description, task_type = task_data
                today = datetime.now().strftime("%Y-%m-%d")
                cursor.execute("INSERT INTO completed_tasks (task_id, task_text, task_description, task_type, completed_date) VALUES (?, ?, ?, ?, ?)", 
                              (task_id, task_text, task_description, task_type, today))
            
            if task_type == 'single':
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            
            conn.commit()
        except Exception as e:
            print(f"Database error: {e}")
            raise e
        finally:
            conn.close()
    
    def get_completed_tasks(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT task_id, task_text, task_description, task_type, completed_date 
            FROM completed_tasks 
            ORDER BY completed_date DESC
        ''')
        tasks = cursor.fetchall()
        conn.close()
        return tasks
    
    def get_task_status(self, task_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT date, completed FROM calendar_tasks WHERE task_id = ?", (task_id,))
        calendar_entries = cursor.fetchall()
        
        # Check if there are completed tasks for this task_id
        has_completed = any(completed for _, completed in calendar_entries)
        if has_completed:
            return "completed"
        
        if not calendar_entries:
            return "unassigned"
        
        today = datetime.now().strftime("%Y-%m-%d")
        for date, completed in calendar_entries:
            if date < today and not completed:
                return "overdue"
        
        return "assigned"
    
    def get_tasks_without_folders(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.id, t.text, t.description, t.task_type
            FROM tasks t
            LEFT JOIN task_folders tf ON t.id = tf.task_id
            WHERE tf.task_id IS NULL
        ''')
        tasks = cursor.fetchall()
        conn.close()
        return tasks

    def delete_completed_task(self, task_id):
        """Delete task from completed_tasks table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM completed_tasks WHERE task_id = ?", (task_id,))
        conn.commit()
        conn.close()

    def get_unassigned_tasks(self):
        """Get tasks that are not in any folder and not in calendar"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.id, t.text, t.description, t.task_type
            FROM tasks t
            LEFT JOIN task_folders tf ON t.id = tf.task_id
            LEFT JOIN calendar_tasks ct ON t.id = ct.task_id
            WHERE tf.task_id IS NULL AND ct.task_id IS NULL
        ''')
        tasks = cursor.fetchall()
        conn.close()
        return tasks

    def debug_calendar_tasks(self, date):
        """Debug method to see calendar tasks for a date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ct.id, ct.task_id, ct.date, ct.completed, t.text 
            FROM calendar_tasks ct
            JOIN tasks t ON ct.task_id = t.id
            WHERE ct.date = ?
        ''', (date,))
        tasks = cursor.fetchall()
        conn.close()
        return tasks