import sqlite3
from datetime import datetime
from typing import List, Optional
from habit import Habit

def initialize_database(db_path: str = 'habits.db') -> sqlite3.Connection:
    """
    Initialize the SQLite database with required tables.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        sqlite3.Connection: Database connection
    """
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Create habits table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            name TEXT PRIMARY KEY,
            task TEXT NOT NULL,
            periodicity TEXT NOT NULL,
            creation_date TEXT NOT NULL
        )
    ''')
    
    # Create habit completions table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_name TEXT NOT NULL,
            completion_time TEXT NOT NULL,
            FOREIGN KEY (habit_name) REFERENCES habits (name)
        )
    ''')
    
    connection.commit()
    return connection

def create_tables(connection: sqlite3.Connection) -> None:
    """
    Create tables in an existing database connection.
    
    Args:
        connection: Existing SQLite database connection
    """
    cursor = connection.cursor()
    
    # Create habits table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            name TEXT PRIMARY KEY,
            task TEXT NOT NULL,
            periodicity TEXT NOT NULL,
            creation_date TEXT NOT NULL
        )
    ''')
    
    # Create habit completions table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_name TEXT NOT NULL,
            completion_time TEXT NOT NULL,
            FOREIGN KEY (habit_name) REFERENCES habits (name)
        )
    ''')
    
    connection.commit()

def save_habit(habit: Habit, connection: sqlite3.Connection) -> None:
    """
    Save a habit to the database.
    
    Args:
        habit: Habit object to save
        connection: Database connection
    """
    cursor = connection.cursor()
    
    # Insert or replace habit
    cursor.execute(
        '''
        INSERT OR REPLACE INTO habits (name, task, periodicity, creation_date)
        VALUES (?, ?, ?, ?)
        ''',
        (habit.name, habit.task, habit.periodicity, habit.creation_date.isoformat())
    )
    
    # Save all completions
    for completion in habit.completions:
        cursor.execute(
            '''
            INSERT OR IGNORE INTO habit_completions (habit_name, completion_time)
            VALUES (?, ?)
            ''',
            (habit.name, completion.isoformat())
        )
    
    connection.commit()

def load_habits(connection: sqlite3.Connection) -> List[Habit]:
    """
    Load all habits from the database with their completions.
    
    Args:
        connection: Database connection
        
    Returns:
        List of Habit objects
    """
    cursor = connection.cursor()
    
    # Get all habits
    cursor.execute('SELECT name, task, periodicity, creation_date FROM habits')
    habits_data = cursor.fetchall()
    
    habits = []
    
    for name, task, periodicity, creation_date in habits_data:
        # Get completions for this habit
        cursor.execute(
            'SELECT completion_time FROM habit_completions WHERE habit_name = ? ORDER BY completion_time',
            (name,)
        )
        completions = [row[0] for row in cursor.fetchall()]
        
        habit = Habit(
            name=name,
            task=task,
            periodicity=periodicity,
            creation_date=datetime.fromisoformat(creation_date),
            completions=[datetime.fromisoformat(c) for c in completions],
            db_connection=connection
        )
        habits.append(habit)
    
    return habits

def delete_habit(habit_name: str, connection: sqlite3.Connection) -> None:
    """
    Delete a habit and its completions from the database.
    
    Args:
        habit_name: Name of the habit to delete
        connection: Database connection
    """
    cursor = connection.cursor()
    
    cursor.execute('DELETE FROM habit_completions WHERE habit_name = ?', (habit_name,))
    cursor.execute('DELETE FROM habits WHERE name = ?', (habit_name,))
    
    connection.commit()

def create_predefined_habits(connection: sqlite3.Connection) -> None:
    """
    Create 5 predefined habits (3 daily and 2 weekly) with example tracking data.
    """
    from datetime import datetime, timedelta
    
    predefined_habits = [
        {
            'name': 'Morning Exercise',
            'task': 'Do 20 minutes of exercise',
            'periodicity': 'daily',
            'completions': [(datetime.now() - timedelta(days=i)).replace(hour=8, minute=0) 
                            for i in range(14)]  # Completed for last 14 days
        },
        {
            'name': 'Read Book',
            'task': 'Read 10 pages of a book',
            'periodicity': 'daily',
            'completions': [(datetime.now() - timedelta(days=i)).replace(hour=21, minute=0) 
                            for i in range(0, 28, 2)]  # Every other day for 28 days
        },
        {
            'name': 'Drink Water',
            'task': 'Drink 2 liters of water',
            'periodicity': 'daily',
            'completions': [(datetime.now() - timedelta(days=i)).replace(hour=12, minute=0) 
                            for i in range(0, 7)]  # Last 7 days
        },
        {
            'name': 'Weekly Review',
            'task': 'Review goals and plan next week',
            'periodicity': 'weekly',
            'completions': [(datetime.now() - timedelta(weeks=i)).replace(hour=10, minute=0) 
                           for i in range(6)]  # Last 6 weeks
        },
        {
            'name': 'Family Dinner',
            'task': 'Have dinner with family',
            'periodicity': 'weekly',
            'completions': [(datetime.now() - timedelta(weeks=i)).replace(hour=19, minute=0) 
                           for i in range(0, 8, 2)]  # Every other week for 8 weeks
        }
    ]
    
    for habit_data in predefined_habits:
        habit = Habit(
            name=habit_data['name'],
            task=habit_data['task'],
            periodicity=habit_data['periodicity'],
            completions=habit_data['completions'],
            db_connection=connection
        )
        save_habit(habit, connection)