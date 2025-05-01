import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class Habit:
    """
    A class representing a habit to be tracked.
    """
    
    def __init__(self, name: str, task: str, periodicity: str, 
                 creation_date: Optional[datetime] = None, 
                 completions: Optional[List[datetime]] = None,
                 db_connection: Optional[sqlite3.Connection] = None):
        self.name = name
        self.task = task
        self.periodicity = periodicity.lower()
        self.creation_date = creation_date if creation_date else datetime.now()
        self.completions = completions if completions else []
        self.db_connection = db_connection
        
        if self.periodicity not in ['daily', 'weekly']:
            raise ValueError("Periodicity must be 'daily' or 'weekly'")
    
    def complete(self) -> None:
        """Mark the habit as completed at the current time."""
        completion_time = datetime.now()
        self.completions.append(completion_time)
        
        if self.db_connection:
            cursor = self.db_connection.cursor()
            # First save the habit if it doesn't exist
            cursor.execute(
                "INSERT OR IGNORE INTO habits (name, task, periodicity, creation_date) VALUES (?, ?, ?, ?)",
                (self.name, self.task, self.periodicity, self.creation_date.isoformat())
            )
            # Then save the completion
            cursor.execute(
                "INSERT INTO habit_completions (habit_name, completion_time) VALUES (?, ?)",
                (self.name, completion_time.isoformat())
            )
            self.db_connection.commit()
    
    def is_completed_for_period(self, date: datetime) -> bool:
        """Check if the habit was completed for the given period."""
        if self.periodicity == 'daily':
            day_start = datetime(date.year, date.month, date.day)
            day_end = day_start + timedelta(days=1)
            return any(day_start <= c < day_end for c in self.completions)
        else:  # weekly
            week_start = date - timedelta(days=date.weekday())
            week_start = datetime(week_start.year, week_start.month, week_start.day)
            week_end = week_start + timedelta(weeks=1)
            return any(week_start <= c < week_end for c in self.completions)
    
    def current_streak(self) -> int:
        """Calculate the current streak of consecutive completed periods."""
        if not self.completions:
            return 0
            
        now = datetime.now()
        sorted_completions = sorted(self.completions, reverse=True)
        most_recent = sorted_completions[0]
        
        if self.periodicity == 'daily':
            # For daily habits, if most recent completion was yesterday, it counts as streak 1
            delta = (now.date() - most_recent.date()).days
            if delta <= 1:  # Completed today or yesterday
                return 1
        else:
            # For weekly habits, if most recent completion was last week, it counts as streak 1
            current_week = now.isocalendar()[1]
            current_year = now.isocalendar()[0]
            last_week = current_week - 1 if current_week > 1 else 52
            last_year = current_year if current_week > 1 else current_year - 1
            
            most_recent_week = most_recent.isocalendar()[1]
            most_recent_year = most_recent.isocalendar()[0]
            
            if (most_recent_year == current_year and most_recent_week == current_week) or \
               (most_recent_year == last_year and most_recent_week == last_week):
                return 1
        
        return 0

    def longest_streak(self) -> int:
        """Calculate the longest streak of consecutive completed periods."""
        if not self.completions:
            return 0
            
        sorted_completions = sorted(self.completions)
        max_streak = 1
        current_streak = 1
        
        if self.periodicity == 'daily':
            for i in range(1, len(sorted_completions)):
                delta = (sorted_completions[i].date() - sorted_completions[i-1].date()).days
                if delta == 1:
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                elif delta > 1:
                    current_streak = 1
        else:
            for i in range(1, len(sorted_completions)):
                prev_year, prev_week, _ = sorted_completions[i-1].isocalendar()
                curr_year, curr_week, _ = sorted_completions[i].isocalendar()
                
                # Calculate week difference considering year boundaries
                if curr_year == prev_year:
                    week_diff = curr_week - prev_week
                else:
                    week_diff = (52 - prev_week) + curr_week
                    
                if week_diff == 1:
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                elif week_diff > 1:
                    current_streak = 1
        
        return max_streak
    
    def to_dict(self) -> Dict:
        """
        Convert the habit to a dictionary representation.
        
        Returns:
            dict: Dictionary containing habit data
        """
        return {
            'name': self.name,
            'task': self.task,
            'periodicity': self.periodicity,
            'creation_date': self.creation_date.isoformat(),
            'completions': [c.isoformat() for c in self.completions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict, db_connection: Optional[sqlite3.Connection] = None):
        """
        Create a Habit object from a dictionary.
        
        Args:
            data: Dictionary containing habit data
            db_connection: Optional database connection
            
        Returns:
            Habit: A Habit object
        """
        return cls(
            name=data['name'],
            task=data['task'],
            periodicity=data['periodicity'],
            creation_date=datetime.fromisoformat(data['creation_date']),
            completions=[datetime.fromisoformat(c) for c in data['completions']],
            db_connection=db_connection
        )