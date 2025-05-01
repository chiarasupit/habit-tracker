import pytest
import sqlite3
from datetime import datetime, timedelta
from habit import Habit
from database import create_tables, save_habit, load_habits, delete_habit
from analytics import (get_all_habits, get_habits_by_periodicity, 
                      get_longest_streak_all, get_longest_streak_habit,
                      get_most_struggled_habits)

@pytest.fixture
def test_db():
    """Fixture to create an in-memory database for testing."""
    connection = sqlite3.connect(':memory:')
    create_tables(connection)
    yield connection
    connection.close()

@pytest.fixture
def sample_habits(test_db):
    """Fixture to create sample habits for testing."""
    now = datetime.now()
    habits = [
        Habit(
            name='Exercise',
            task='30 minutes workout',
            periodicity='daily',
            completions=[
                now - timedelta(days=1),
                now - timedelta(days=2),
                now - timedelta(days=3)
            ],
            db_connection=test_db
        ),
        Habit(
            name='Read',
            task='Read 20 pages',
            periodicity='daily',
            completions=[
                now - timedelta(days=1),
                now - timedelta(weeks=1),
                now - timedelta(weeks=2)
            ],
            db_connection=test_db
        ),
        Habit(
            name='Weekly Review',
            task='Review weekly goals',
            periodicity='weekly',
            completions=[
                now - timedelta(weeks=1),
                now - timedelta(weeks=2),
                now - timedelta(weeks=3)
            ],
            db_connection=test_db
        )
    ]
    
    for habit in habits:
        save_habit(habit, test_db)
    
    return habits

def test_habit_creation():
    """Test creating a Habit object."""
    habit = Habit('Test', 'Test task', 'daily')
    assert habit.name == 'Test'
    assert habit.task == 'Test task'
    assert habit.periodicity == 'daily'
    assert isinstance(habit.creation_date, datetime)
    assert len(habit.completions) == 0

def test_habit_completion(test_db):
    """Test completing a habit."""
    habit = Habit('Test', 'Test task', 'daily', db_connection=test_db)
    habit.complete()
    assert len(habit.completions) == 1
    assert isinstance(habit.completions[0], datetime)
    
    # Verify it was saved to database
    loaded_habits = load_habits(test_db)
    assert len(loaded_habits) == 1
    assert len(loaded_habits[0].completions) == 1

def test_habit_streak_daily():
    """Test streak calculation for daily habits."""
    now = datetime.now()
    habit = Habit(
        'Test', 
        'Test task', 
        'daily',
        completions=[
            now - timedelta(days=1),
            now - timedelta(days=2),
            now - timedelta(days=3)
        ]
    )
    assert habit.current_streak() == 1  # Only completed today would count as streak 1
    assert habit.longest_streak() == 3  # 3 consecutive days

def test_habit_streak_weekly():
    """Test streak calculation for weekly habits."""
    now = datetime.now()
    habit = Habit(
        'Test', 
        'Test task', 
        'weekly',
        completions=[
            now - timedelta(weeks=1),
            now - timedelta(weeks=2),
            now - timedelta(weeks=3)
        ]
    )
    assert habit.current_streak() == 1  # Only this week counts as streak 1
    assert habit.longest_streak() == 3  # 3 consecutive weeks

def test_save_and_load_habits(test_db, sample_habits):
    """Test saving and loading habits from database."""
    loaded_habits = load_habits(test_db)
    assert len(loaded_habits) == 3
    
    # Verify habit data
    for original, loaded in zip(sample_habits, loaded_habits):
        assert original.name == loaded.name
        assert original.task == loaded.task
        assert original.periodicity == loaded.periodicity
        assert len(original.completions) == len(loaded.completions)

def test_delete_habit(test_db, sample_habits):
    """Test deleting a habit from database."""
    delete_habit('Exercise', test_db)
    loaded_habits = load_habits(test_db)
    assert len(loaded_habits) == 2
    assert all(habit.name != 'Exercise' for habit in loaded_habits)

def test_get_all_habits(sample_habits):
    """Test getting all habits."""
    habits_data = get_all_habits(sample_habits)
    assert len(habits_data) == 3
    assert all('name' in habit for habit in habits_data)

def test_get_habits_by_periodicity(sample_habits):
    """Test getting habits by periodicity."""
    daily_habits = get_habits_by_periodicity(sample_habits, 'daily')
    assert len(daily_habits) == 2
    assert all(habit['periodicity'] == 'daily' for habit in daily_habits)
    
    weekly_habits = get_habits_by_periodicity(sample_habits, 'weekly')
    assert len(weekly_habits) == 1
    assert all(habit['periodicity'] == 'weekly' for habit in weekly_habits)

def test_get_longest_streak_all(sample_habits):
    """Test getting longest streak among all habits."""
    result = get_longest_streak_all(sample_habits)
    assert 'habit' in result
    assert 'streak' in result
    assert result['streak'] == 3  # From the weekly habit with 3 completions

def test_get_longest_streak_habit(sample_habits):
    """Test getting longest streak for a specific habit."""
    result = get_longest_streak_habit(sample_habits, 'Exercise')
    assert result['habit'] == 'Exercise'
    assert result['streak'] == 3

def test_get_most_struggled_habits(sample_habits):
    """Test getting most struggled habits."""
    results = get_most_struggled_habits(sample_habits, days=30)
    assert len(results) == 3
    assert all('missed_periods' in r for r in results)
    assert all('total_periods' in r for r in results)