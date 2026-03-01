# database.py
import sqlite3
import json
from datetime import datetime, timedelta
from config import Config

class Database:
    def __init__(self, db_path="duty_schedule.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # People table with new columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                duty_count INTEGER DEFAULT 0,
                vpi_count INTEGER DEFAULT 0,
                guard_count INTEGER DEFAULT 0,
                is_senior INTEGER DEFAULT 0,
                is_wounded INTEGER DEFAULT 0,
                is_commander INTEGER DEFAULT 0
            )
        ''')
        
        # Schedule table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                duty_person TEXT,
                vpi_person TEXT,
                guard_people TEXT,
                UNIQUE(date)
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL
            )
        ''')
        
        # Insert default settings if not exists
        default_settings = [
            ('training_day', Config.DEFAULT_TRAINING_DAY),
            ('duty_per_week', str(Config.DEFAULT_DUTY_PER_WEEK)),
            ('vpi_per_week', str(Config.DEFAULT_VPI_PER_WEEK)),
            ('guard_count', str(Config.DEFAULT_GUARD_COUNT)),
            ('people_count', str(Config.DEFAULT_PEOPLE_COUNT)),
            ('start_date', Config.START_DATE),
            ('end_date', Config.END_DATE),
            ('guard_frequency', str(Config.DEFAULT_GUARD_FREQUENCY)),  # CHANGED FROM duty_frequency
            ('first_duty_date', Config.DEFAULT_FIRST_DUTY_DATE)
        ]
        
        for key, value in default_settings:
            cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, value))
        
        # Migrate existing people table if needed
        cursor.execute("PRAGMA table_info(people)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'is_senior' not in columns:
            cursor.execute('ALTER TABLE people ADD COLUMN is_senior INTEGER DEFAULT 0')
        if 'is_wounded' not in columns:
            cursor.execute('ALTER TABLE people ADD COLUMN is_wounded INTEGER DEFAULT 0')
        if 'is_commander' not in columns:
            cursor.execute('ALTER TABLE people ADD COLUMN is_commander INTEGER DEFAULT 0')
        
        conn.commit()
        conn.close()
    
    def get_people(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name, duty_count, vpi_count, guard_count, is_senior, is_wounded, is_commander FROM people ORDER BY name')
        people = cursor.fetchall()
        conn.close()
        return people
    
    def save_people(self, people_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing people
        cursor.execute('DELETE FROM people')
        
        # Insert new people
        for person in people_data:
            cursor.execute(
                'INSERT INTO people (name, duty_count, vpi_count, guard_count, is_senior, is_wounded, is_commander) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (person[0], person[1], person[2], person[3], person[4], person[5], person[6])
            )
        
        conn.commit()
        conn.close()
    
    def get_schedule(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT date, duty_person, vpi_person, guard_people FROM schedule ORDER BY date')
        schedule = cursor.fetchall()
        conn.close()
        
        # Parse JSON for guard_people
        result = []
        for row in schedule:
            guard_people = json.loads(row[3]) if row[3] else []
            result.append((row[0], row[1], row[2], guard_people))
        return result
    
    def save_schedule(self, schedule_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing schedule
        cursor.execute('DELETE FROM schedule')
        
        # Insert new schedule
        for date, duty_person, vpi_person, guard_people in schedule_data:
            guard_json = json.dumps(guard_people)
            cursor.execute(
                'INSERT INTO schedule (date, duty_person, vpi_person, guard_people) VALUES (?, ?, ?, ?)',
                (date, duty_person, vpi_person, guard_json)
            )
        
        conn.commit()
        conn.close()
    
    def get_setting(self, key):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def save_settings(self, settings):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for key, value in settings.items():
            cursor.execute(
                'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                (key, str(value))
            )
        
        conn.commit()
        conn.close()
    
    def increment_duty_count(self, person_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE people SET duty_count = duty_count + 1 WHERE name = ?', (person_name,))
        conn.commit()
        conn.close()
    
    def increment_vpi_count(self, person_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE people SET vpi_count = vpi_count + 1 WHERE name = ?', (person_name,))
        conn.commit()
        conn.close()
    
    def increment_guard_count(self, person_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE people SET guard_count = guard_count + 1 WHERE name = ?', (person_name,))
        conn.commit()
        conn.close()