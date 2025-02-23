import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Union

class Database:
    def __init__(self, db_path: Union[str, None] = None):
        if db_path is None:
            # Get the current working directory
            current_dir = os.getcwd()
            # Create a data directory in the current working directory
            db_path = os.path.join(current_dir, 'data', 'error404.db')
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        print(f"Using database path: {self.db_path}")  # Debug print
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS tasks
                            (id INTEGER PRIMARY KEY,
                             title TEXT NOT NULL,
                             description TEXT,
                             priority TEXT,
                             category TEXT,
                             labels TEXT,  -- Store as comma-separated values
                             deadline TEXT,
                             status TEXT DEFAULT 'pending',
                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Attempting to use database at: {self.db_path}")
            raise

    def add_task(self, title: str, description: Optional[str] = None, 
                 priority: Optional[str] = None, category: Optional[str] = None,
                 labels: Optional[str] = None, deadline: Optional[str] = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO tasks 
                        (title, description, priority, category, labels, deadline)
                        VALUES (?, ?, ?, ?, ?, ?)''', 
                     (title, description, priority, category, labels, deadline))
            conn.commit()
            return c.lastrowid

    def get_all_tasks(self) -> List[Dict]:
        try:
            with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute('''SELECT 
                            id,
                            COALESCE(title, '') as title,
                            COALESCE(description, '') as description,
                            COALESCE(priority, 'Low') as priority,
                            COALESCE(deadline, '') as deadline,
                            COALESCE(status, 'pending') as status,
                            COALESCE(category, 'Uncategorized') as category,
                            COALESCE(labels, 'Uncategorized') as labels
                         FROM tasks''')
                tasks = [dict(row) for row in c.fetchall()]
                print(f"Database - Retrieved {len(tasks)} tasks")
                return tasks
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            return []

    def update_task_status(self, task_id: int, new_status: str):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''UPDATE tasks 
                       SET status = ?
                       WHERE id = ?''',
                    (new_status, task_id))
            conn.commit()

    def remove_completed_tasks(self):
        """Permanently delete completed tasks from database"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM tasks WHERE status = 'completed'")
            conn.commit()
            return c.rowcount  # Returns number of tasks deleted

    def cleanup_completed_tasks(self):
        """Remove all completed tasks from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE status = 'Completed'")
            return cursor.rowcount 

    def execute_query(self, query, params=None):
        """
        Execute a SQL query with optional parameters.
        """
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query) 