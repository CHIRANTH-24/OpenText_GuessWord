"""Setup verification script."""
import os
import sys


def check_environment():
    """Check if environment is properly configured."""
    print("Checking environment setup...")

    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ required")
        return False
    print("✓ Python version OK")

    # Check if virtual environment is active
    if not hasattr(sys, "real_prefix") and not (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("⚠️  Virtual environment not detected (recommended)")
    else:
        print("✓ Virtual environment active")

    # Check if .env exists
    if not os.path.exists(".env"):
        print("⚠️  .env file not found (using defaults)")
    else:
        print("✓ .env file found")

    # Check if db.sqlite3 exists
    if not os.path.exists("db.sqlite3"):
        print("⚠️  Database not found - run: python manage.py migrate")
    else:
        print("✓ Database exists")

    print("\nSetup appears ready!")
    print("\nNext steps:")
    print("1. python manage.py migrate")
    print("2. python manage.py createsuperuser")
    print("3. python manage.py seed_words")
    print("4. python manage.py runserver")

    return True


if __name__ == "__main__":
    check_environment()

