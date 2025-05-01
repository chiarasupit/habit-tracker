# 🧠 Habit Tracker Application

A Python-based habit tracking system that helps users build and maintain positive habits through periodic tracking and analytics.

## 📑 Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

## ✅ Features

### Core Functionality
- ✅ Create daily/weekly habits  
- ✅ Track habit completions  
- ✅ Delete unwanted habits  
- ✅ SQLite database storage  

### Analytics
- 📊 Current and longest streaks  
- 🔍 Filter habits by periodicity  
- ❗ Identify struggling habits  

## 💾 Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/chiarasupit/habit-tracker.git
   cd habit-tracker

2. **Set up virtual environment**:
python -m venv venv
- Windows:
venv\Scripts\activate
- MacOS/Linux:
source venv/bin/activate

3. **Install dependencies**:
pip install -r requirements.txt

## 🚀 Usage
Start the application:
python main.py

### Main Menu Options
1. Create new habit
2. Complete a habit
3. Delete a habit
4. View all habits
5. View by periodicity
6. View streak analytics
7. View struggling habits
8. Load test data
9. Exit

## 🧪 Testing
Run all tests:
pytest test.py -v

Test Coverage Includes:
1. Habit creation/deletion
2. Streak calculations
3. Database operations
4. Analytics functions
 
## 🛠️ Troubleshooting
1. Database errors -> Delete habits.db file
2. Import errors ->	Reinstall dependencies
3. Test failures -> Check system date/time settings
