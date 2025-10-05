# Quick Start Guide

Get up and running with Guess The Word in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

## Setup Steps

### 1. Create and Activate Virtual Environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
python manage.py migrate
```

### 4. Create Admin User

```bash
python manage.py createsuperuser
```

Enter your desired username, email (optional), and password when prompted.

**Example:**

- Username: `Admin1` (must have mixed case)
- Password: `admin1@` (must meet requirements)

### 5. Seed Words

```bash
python manage.py seed_words
```

This adds 20 words to the database for the game.

### 6. Run the Server

```bash
python manage.py runserver
```

### 7. Access the Application

Open your browser and navigate to:

- **Game**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

## First Time Usage

### As a Player

1. Click "Sign Up" on the home page
2. Create an account:
   - Username: At least 5 characters with both upper and lower case (e.g., `TestUser`)
   - Password: At least 5 characters with a letter, digit, and special char (e.g., `test1@`)
3. Log in with your credentials
4. Click "Start New Game"
5. Enter 5-letter words to guess
6. Play up to 3 games per day!

### As an Admin

1. Go to http://localhost:8000/admin
2. Log in with your superuser credentials
3. Explore:
   - **Games**: View all games and their outcomes
   - **Words**: Manage the word list
   - **Daily Quotas**: Monitor user activity
   - **Reports**: Access daily and user reports at http://localhost:8000/reports/daily

## Testing

Run the test suite to verify everything is working:

```bash
pytest
```

Expected output: All tests passing ✓

## Common Issues

### Issue: "No module named 'django'"

**Solution**: Make sure you've activated the virtual environment and installed requirements.

### Issue: "relation does not exist"

**Solution**: Run `python manage.py migrate` to create database tables.

### Issue: "No words available"

**Solution**: Run `python manage.py seed_words` to add words to the database.

### Issue: Can't log in

**Solution**: Verify your username has both upper and lower case letters, and password meets requirements (≥5 chars, has letter, digit, and one of: $ % \* @).

## Next Steps

- Add more words via the admin panel
- View reports to track user activity
- Customize the word list for different difficulty levels
- Export game data as CSV for analysis

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Deactivating Virtual Environment

```bash
deactivate
```

---

For detailed information, see [README.md](README.md)
