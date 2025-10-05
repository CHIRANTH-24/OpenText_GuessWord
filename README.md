# Guess The Word - Wordle-style Game

A production-quality Wordle-style word guessing game built with Django 5.x, featuring user authentication, daily game limits, and comprehensive admin reporting.

**Deployed**: https://chiranthrajuc.pythonanywhere.com/

## Features

- **User Authentication**: Secure registration and login with custom validation rules
- **Game Mechanics**:
  - Guess a 5-letter word in up to 5 attempts
  - Color-coded feedback (green/orange/grey) after each guess
  - Play up to 3 games per day
- **Admin Reports**:
  - Daily activity reports with CSV export
  - Per-user statistics and performance tracking
- **Security**: CSRF protection, input validation, and proper authorization
- **Testing**: Comprehensive test suite with pytest

## Tech Stack

- **Backend**: Python 3.11+, Django 5.x
- **Frontend**: Django templates, HTMX, plain CSS
- **Database**: SQLite (dev), PostgreSQL (production via DATABASE_URL)
- **Authentication**: Django's built-in user model
- **Testing**: pytest, pytest-django, factory-boy
- **Linting**: ruff, black

## Project Structure

```
guessword/
├── .github/workflows/      # CI/CD configuration
├── accounts/               # User authentication
│   ├── forms.py           # Custom registration forms
│   ├── views.py           # Auth views
│   └── templates/         # Login/signup templates
├── game/                  # Core game logic
│   ├── models.py          # Word, Game, Guess, DailyQuota models
│   ├── views.py           # Game and report views
│   ├── forms.py           # Guess form
│   ├── utils.py           # Coloring logic
│   ├── admin.py           # Django admin configuration
│   ├── management/        # Management commands
│   │   └── commands/
│   │       └── seed_words.py
│   ├── static/css/        # Stylesheets
│   ├── templates/         # Game templates
│   └── tests/             # Comprehensive test suite
├── guessword/             # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── pyproject.toml        # ruff/black config
└── README.md
```

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd guessword
```

### 2. Create Virtual Environment

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

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and set your configuration:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
TIME_ZONE=UTC

# For production PostgreSQL (optional):
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. Seed Words

```bash
python manage.py seed_words
```

This command seeds the database with 20 5-letter words.

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit http://localhost:8000 to access the application.

## Usage

### Playing the Game

1. **Sign Up**: Create an account with:

   - Username: ≥5 characters with both uppercase and lowercase letters
   - Password: ≥5 characters with at least one letter, one digit, and one of: $ % \* @

2. **Login**: Use your credentials to access the game

3. **Start a Game**: Click "Start New Game" from the home page

4. **Make Guesses**:

   - Enter a 5-letter word
   - View color-coded feedback:
     - 🟩 Green: Correct letter in correct position
     - 🟧 Orange: Correct letter in wrong position
     - ⬜ Grey: Letter not in word

5. **Daily Limit**: You can play up to 3 games per calendar day

### Admin Features

Access the admin panel at http://localhost:8000/admin

- **View Games**: Monitor all games with status and outcomes
- **Manage Words**: Add or remove words from the word list
- **Reports**:
  - Daily Report: http://localhost:8000/reports/daily
  - User Report: http://localhost:8000/reports/user
- **Export Data**: Download CSV reports for analysis

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest game/tests/test_game_flow.py
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage

```bash
pytest --cov=game --cov=accounts
```

## Code Quality

### Run Linter (ruff)

```bash
ruff check .
```

### Format Code (black)

```bash
black .
```

### Check Formatting

```bash
black --check .
```

## Deployment

### PostgreSQL Setup

For production, configure PostgreSQL via `DATABASE_URL`:

```env
DATABASE_URL=postgresql://username:password@host:port/database
```

The application will automatically use PostgreSQL when `DATABASE_URL` is set.

### Environment Variables for Production

```env
SECRET_KEY=<strong-random-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://...
TIME_ZONE=America/New_York
```

### Static Files

Collect static files for production:

```bash
python manage.py collectstatic --noinput
```

### Run Migrations

```bash
python manage.py migrate --noinput
```

### Create Superuser (Non-interactive)

```bash
python manage.py createsuperuser --noinput --username admin --email admin@example.com
```

## API Endpoints

- `/` - Home page
- `/accounts/signup/` - User registration
- `/accounts/login/` - User login
- `/accounts/logout/` - User logout
- `/game/start/` - Start new game (POST)
- `/game/<id>/` - Game board
- `/game/<id>/guess/` - Submit guess (POST, HTMX)
- `/reports/daily/` - Daily report (admin only)
- `/reports/user/` - User report (admin only)
- `/admin/` - Django admin panel

## Validation Rules

### Username

- Minimum 5 characters
- Must contain at least one uppercase letter
- Must contain at least one lowercase letter
- Must be unique

### Password

- Minimum 5 characters
- Must contain at least one letter
- Must contain at least one digit
- Must contain at least one of: $ % \* @

### Guess

- Exactly 5 letters
- Only alphabetic characters
- Automatically converted to uppercase

## Game Rules

1. Each game uses a random 5-letter word from the database
2. Players have up to 5 guesses to find the word
3. Each guess must be exactly 5 letters
4. After each guess, colored feedback is provided
5. Players can start up to 3 games per calendar day
6. Games must be completed before starting a new one

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and ensure tests pass: `pytest`
4. Run linters: `ruff check . && black --check .`
5. Commit your changes: `git commit -am 'Add new feature'`
6. Push to the branch: `git push origin feature/new-feature`
7. Submit a pull request

## CI/CD

The project uses GitHub Actions for continuous integration:

- **Linting**: ruff and black checks
- **Testing**: Full test suite execution
- **Database**: Automatic migrations and seeding

Workflow triggers on:

- Push to main branch
- Pull requests to main branch

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

- Inspired by Wordle by Josh Wardle
- Built with Django and HTMX
- Tested with pytest

---

**Note**: This is a learning/demonstration project. For production use, ensure proper security configurations, use environment-specific settings, and implement additional monitoring and logging.
