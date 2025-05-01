import sqlite3
from datetime import datetime
from typing import List, Optional
from habit import Habit
from database import initialize_database, load_habits, save_habit, delete_habit, create_predefined_habits
from analytics import (
    get_all_habits, 
    get_habits_by_periodicity, 
    get_longest_streak_all, 
    get_longest_streak_habit,
    get_most_struggled_habits
)

class HabitTrackerCLI:
    """Command Line Interface for the Habit Tracker application."""
    
    def __init__(self, db_path: str = 'habits.db'):
        """Initialize the CLI with a database connection."""
        self.connection = initialize_database(db_path)
        self.habits = load_habits(self.connection)
        self.running = True
    
    def run(self):
        """Run the main CLI loop."""
        print("Welcome to the Habit Tracker!")
        
        while self.running:
            self.display_menu()
            choice = input("Enter your choice: ")
            self.handle_choice(choice)
    
    def display_menu(self):
        """Display the main menu options."""
        print("\nMain Menu:")
        print("1. Create a new habit")
        print("2. Complete a habit")
        print("3. Delete a habit")
        print("4. View all habits")
        print("5. View habits by periodicity")
        print("6. View longest streaks")
        print("7. View most struggled habits")
        print("8. Load predefined habits (for testing)")
        print("9. Exit")
    
    def handle_choice(self, choice: str):
        """Handle user menu choice."""
        try:
            if choice == '1':
                self.create_habit()
            elif choice == '2':
                self.complete_habit()
            elif choice == '3':
                self.delete_habit()
            elif choice == '4':
                self.view_all_habits()
            elif choice == '5':
                self.view_habits_by_periodicity()
            elif choice == '6':
                self.view_longest_streaks()
            elif choice == '7':
                self.view_most_struggled_habits()
            elif choice == '8':
                self.load_predefined_habits()
            elif choice == '9':
                self.exit()
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def create_habit(self):
        """Create a new habit."""
        print("\nCreate a New Habit")
        name = input("Enter habit name: ")
        task = input("Enter task description: ")
        
        while True:
            periodicity = input("Enter periodicity (daily/weekly): ").lower()
            if periodicity in ['daily', 'weekly']:
                break
            print("Invalid periodicity. Please enter 'daily' or 'weekly'.")
        
        habit = Habit(name, task, periodicity, db_connection=self.connection)
        save_habit(habit, self.connection)
        self.habits = load_habits(self.connection)
        print(f"Habit '{name}' created successfully!")
    
    def complete_habit(self):
        """Mark a habit as completed."""
        if not self.habits:
            print("No habits available. Please create a habit first.")
            return
        
        print("\nComplete a Habit")
        self.list_habits_with_numbers()
        
        try:
            choice = int(input("Enter the number of the habit to complete: ")) - 1
            if 0 <= choice < len(self.habits):
                self.habits[choice].complete()
                print(f"Habit '{self.habits[choice].name}' marked as completed!")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a valid number.")
    
    def delete_habit(self):
        """Delete a habit."""
        if not self.habits:
            print("No habits available to delete.")
            return
        
        print("\nDelete a Habit")
        self.list_habits_with_numbers()
        
        try:
            choice = int(input("Enter the number of the habit to delete: ")) - 1
            if 0 <= choice < len(self.habits):
                habit_name = self.habits[choice].name
                delete_habit(habit_name, self.connection)
                self.habits = load_habits(self.connection)
                print(f"Habit '{habit_name}' deleted successfully!")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a valid number.")
    
    def view_all_habits(self):
        """Display all habits."""
        if not self.habits:
            print("No habits available.")
            return
        
        print("\nAll Habits:")
        habits_data = get_all_habits(self.habits)
        for i, habit in enumerate(habits_data, 1):
            print(f"{i}. {habit['name']} - {habit['task']} ({habit['periodicity']})")
            print(f"   Created: {habit['creation_date']}")
            print(f"   Completions: {len(habit['completions'])}")
            print(f"   Current streak: {Habit.from_dict(habit).current_streak()}")
    
    def view_habits_by_periodicity(self):
        """Display habits filtered by periodicity."""
        if not self.habits:
            print("No habits available.")
            return
        
        periodicity = input("Enter periodicity to filter by (daily/weekly): ").lower()
        if periodicity not in ['daily', 'weekly']:
            print("Invalid periodicity. Please enter 'daily' or 'weekly'.")
            return
        
        habits_data = get_habits_by_periodicity(self.habits, periodicity)
        print(f"\n{periodicity.capitalize()} Habits:")
        
        if not habits_data:
            print(f"No {periodicity} habits available.")
            return
        
        for i, habit in enumerate(habits_data, 1):
            print(f"{i}. {habit['name']} - {habit['task']}")
            print(f"   Completions: {len(habit['completions'])}")
            print(f"   Current streak: {Habit.from_dict(habit).current_streak()}")
    
    def view_longest_streaks(self):
        """Display longest streak information."""
        if not self.habits:
            print("No habits available.")
            return
        
        print("\nLongest Streaks:")
        
        # Longest streak among all habits
        all_streak = get_longest_streak_all(self.habits)
        print(f"Longest streak among all habits: {all_streak['streak']} periods ({all_streak['habit']})")
        
        # Longest streak for each habit
        print("\nLongest streaks for individual habits:")
        for habit in self.habits:
            streak = habit.longest_streak()
            print(f"- {habit.name}: {streak} periods")
        
        # Option to view streak for specific habit
        print("\nView streak for a specific habit:")
        self.list_habits_with_numbers()
        
        try:
            choice = input("Enter the number of the habit (or press Enter to skip): ")
            if choice:
                choice = int(choice) - 1
                if 0 <= choice < len(self.habits):
                    habit = self.habits[choice]
                    streak = habit.longest_streak()
                    print(f"\nLongest streak for '{habit.name}': {streak} periods")
                else:
                    print("Invalid choice.")
        except ValueError:
            print("Please enter a valid number.")
    
    def view_most_struggled_habits(self):
        """Display habits with most missed periods."""
        if not self.habits:
            print("No habits available.")
            return
        
        try:
            days = int(input("Enter number of days to analyze (default 30): ") or 30)
        except ValueError:
            print("Invalid input. Using default 30 days.")
            days = 30
        
        results = get_most_struggled_habits(self.habits, days)
        
        print(f"\nMost struggled habits in the last {days} days:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['habit']} ({result['periodicity']})")
            print(f"   Missed periods: {result['missed_periods']} out of {result['total_periods']}")
    
    def load_predefined_habits(self):
        """Load predefined habits for testing."""
        create_predefined_habits(self.connection)
        self.habits = load_habits(self.connection)
        print("Predefined habits loaded successfully!")
    
    def list_habits_with_numbers(self):
        """Display a numbered list of habits."""
        for i, habit in enumerate(self.habits, 1):
            print(f"{i}. {habit.name} - {habit.task} ({habit.periodicity})")
    
    def exit(self):
        """Clean up and exit the application."""
        self.connection.close()
        self.running = False
        print("Goodbye!")

if __name__ == "__main__":
    cli = HabitTrackerCLI()
    cli.run()