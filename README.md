# StudyBuddy
📚 A smart study planner &amp; focus tracker with task management, Pomodoro timer, and analytics — built with Flask, SQLAlchemy &amp; SQLite
✨ Features
Task Planner — add tasks with due dates, mark them complete, delete them
Pomodoro Focus Timer — 25-min work sessions, 5-min short breaks, 15-min long break every 4 sessions, with full session history logging
Study Analytics — total time studied, sessions per day, average session length, and a completed-vs-pending chart
Interactive Calendar — click any day to see tasks assigned to it
Dark Mode — toggle between light and dark themes
Secure Authentication — login & signup with hashed passwords (never stored in plain text)
Break-Time Games — Tic Tac Toe, Memory Match, Rock Paper Scissors, Snake, and 2048, for when boredom hits

🚀 Getting Started
Prerequisites
Python 3.9+
Installation
bash
# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install flask flask-sqlalchemy flask-login
