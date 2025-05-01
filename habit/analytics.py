from typing import List, Dict
from datetime import datetime, timedelta
from habit import Habit

def get_all_habits(habits: List[Habit]) -> List[Dict]:
    """
    Return a list of all currently tracked habits with their details.
    
    Args:
        habits: List of Habit objects
        
    Returns:
        List of dictionaries with habit details
    """
    return [habit.to_dict() for habit in habits]

def get_habits_by_periodicity(habits: List[Habit], periodicity: str) -> List[Dict]:
    """
    Return a list of all habits with the given periodicity.
    
    Args:
        habits: List of Habit objects
        periodicity: 'daily' or 'weekly'
        
    Returns:
        List of dictionaries with habit details
    """
    return [habit.to_dict() for habit in habits if habit.periodicity == periodicity]

def get_longest_streak_all(habits: List[Habit]) -> Dict:
    """
    Return the longest run streak among all defined habits.
    
    Args:
        habits: List of Habit objects
        
    Returns:
        Dictionary with habit name and streak length
    """
    if not habits:
        return {"habit": None, "streak": 0}
    
    streaks = [(habit.name, habit.longest_streak()) for habit in habits]
    longest = max(streaks, key=lambda x: x[1])
    return {"habit": longest[0], "streak": longest[1]}

def get_longest_streak_habit(habits: List[Habit], habit_name: str) -> Dict:
    """
    Return the longest run streak for a specific habit.
    
    Args:
        habits: List of Habit objects
        habit_name: Name of the habit to check
        
    Returns:
        Dictionary with habit name and streak length
    """
    for habit in habits:
        if habit.name == habit_name:
            return {"habit": habit_name, "streak": habit.longest_streak()}
    return {"habit": habit_name, "streak": 0}

def get_most_struggled_habits(habits: List[Habit], days: int = 30) -> List[Dict]:
    """
    Return habits with the most missed periods in the last X days.
    
    Args:
        habits: List of Habit objects
        days: Number of days to look back (default 30)
        
    Returns:
        List of dictionaries with habit names and missed periods count
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    results = []
    
    for habit in habits:
        missed = 0
        current_date = start_date
        
        if habit.periodicity == 'daily':
            while current_date <= end_date:
                if not habit.is_completed_for_period(current_date):
                    missed += 1
                current_date += timedelta(days=1)
        else:  # weekly
            while current_date <= end_date:
                if not habit.is_completed_for_period(current_date):
                    missed += 1
                current_date += timedelta(weeks=1)
        
        results.append({
            "habit": habit.name,
            "periodicity": habit.periodicity,
            "missed_periods": missed,
            "total_periods": days//7 if habit.periodicity == 'weekly' else days
        })
    
    # Sort by most missed periods
    return sorted(results, key=lambda x: x['missed_periods'], reverse=True)