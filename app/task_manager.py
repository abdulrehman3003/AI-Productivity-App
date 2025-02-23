from datetime import datetime
from typing import List, Dict, Optional
from .database import Database
from .granite_service import GraniteService
import sqlite3

class TaskManager:
    def __init__(self, db: Database, granite: GraniteService):
        self.db = db
        self.granite = granite

    def add_task(self, title: str, description: Optional[str] = None,
                 priority: Optional[str] = None, category: Optional[str] = None,
                 labels: Optional[str] = None, deadline: Optional[str] = None) -> int:
        return self.db.add_task(
            title=title,
            description=description,
            priority=priority,
            category=category,
            labels=labels,
            deadline=deadline
        )

    def get_tasks(self) -> List[Dict]:
        try:
            tasks = self.db.get_all_tasks()
            if not tasks:
                return []
            return self.granite.prioritize_tasks(tasks)
        except Exception as e:
            print(f"Error getting tasks: {str(e)}")
            return []

    def get_insights(self) -> Dict:
        try:
            print("\n" + "="*40)
            print("TaskManager: Starting insights generation")
            tasks = self.db.get_all_tasks()
            
            # Validate tasks format
            if not isinstance(tasks, list):
                print("Invalid tasks format - expected list")
                return self._get_fallback_response()
            
            print(f"Found {len(tasks)} tasks for analysis")
            print("Sample task:", tasks[0] if tasks else "No tasks")
            
            insights = self.granite.generate_insights(tasks)
            
            print("Insights generated successfully")
            print("="*40 + "\n")
            return insights
        
        except Exception as e:
            print(f"Error in get_insights: {str(e)}")
            return {
                "productivity_analysis": "Error generating insights",
                "recommendations": ["Please try again later"],
                "time_management": "Analysis unavailable",
                "priority_distribution": "Data loading failed"
            }

    def check_reminders(self) -> List[Dict]:
        tasks = self.db.get_all_tasks()
        today = datetime.today().strftime('%Y-%m-%d')
        return [task for task in tasks if task['deadline'] == today]

    def get_reminders(self, days_ahead: int = 1) -> List[Dict]:
        """Get tasks due in the next X days"""
        from datetime import datetime, timedelta
        today = datetime.today().date()
        end_date = (today + timedelta(days=days_ahead)).isoformat()
        
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('''SELECT * FROM tasks 
                       WHERE deadline BETWEEN ? AND ?
                       AND status != 'completed'
                       ORDER BY priority DESC''',
                    (today.isoformat(), end_date))
            return [dict(row) for row in c.fetchall()]

    def get_task_insights(self, task: Dict) -> Dict:
        """Get AI-powered insights for a specific task"""
        return self.granite.get_task_insights(task)

    def get_task_guide(self, task: Dict) -> Dict:
        """Get detailed completion guide for a task"""
        return self.granite.generate_task_guide(task)

    def update_task_status(self, task_id: int, new_status: str):
        """Update a task's status in the database"""
        return self.db.update_task_status(task_id, new_status)

    def cleanup_completed_tasks(self) -> int:
        """
        Delete all tasks marked as 'Completed'.
        Returns the number of tasks deleted.
        """
        try:
            # Execute the delete query for completed tasks
            query = "DELETE FROM tasks WHERE status = ?"
            params = ("Completed",)
            self.db.execute_query(query, params)
            
            # Get the number of rows affected
            deleted_count = self.db.cursor.rowcount
            self.db.conn.commit()  # Commit the transaction
            return deleted_count
        except Exception as e:
            print(f"Error deleting completed tasks: {e}")
            return 0 