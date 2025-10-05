"""Tests for authentication and validation."""
import pytest
from django.contrib.auth.models import User

from accounts.forms import SignUpForm


@pytest.mark.django_db
class TestUsernameValidation:
    """Test username validation rules."""

    def test_username_minimum_length(self):
        """Username must be at least 5 characters."""
        form = SignUpForm(
            data={
                "username": "abC",
                "password1": "test1@",
                "password2": "test1@",
            }
        )
        assert not form.is_valid()
        assert "username" in form.errors

    def test_username_requires_uppercase(self):
        """Username must contain at least one uppercase letter."""
        form = SignUpForm(
            data={
                "username": "testuser",
                "password1": "test1@",
                "password2": "test1@",
            }
        )
        assert not form.is_valid()
        assert "username" in form.errors
        assert "uppercase" in str(form.errors["username"]).lower()

    def test_username_requires_lowercase(self):
        """Username must contain at least one lowercase letter."""
        form = SignUpForm(
            data={
                "username": "TESTUSER",
                "password1": "test1@",
                "password2": "test1@",
            }
        )
        assert not form.is_valid()
        assert "username" in form.errors
        assert "lowercase" in str(form.errors["username"]).lower()

    def test_valid_username(self):
        """Valid username with mixed case and sufficient length."""
        form = SignUpForm(
            data={
                "username": "TestUser",
                "password1": "test1@",
                "password2": "test1@",
            }
        )
        assert form.is_valid()

    def test_username_already_exists(self):
        """Username must be unique."""
        User.objects.create_user(username="TestUser", password="test1@")
        form = SignUpForm(
            data={
                "username": "TestUser",
                "password1": "test1@",
                "password2": "test1@",
            }
        )
        assert not form.is_valid()
        assert "username" in form.errors


@pytest.mark.django_db
class TestPasswordValidation:
    """Test password validation rules."""

    def test_password_minimum_length(self):
        """Password must be at least 5 characters."""
        form = SignUpForm(
            data={
                "username": "TestUser",
                "password1": "ab1@",
                "password2": "ab1@",
            }
        )
        assert not form.is_valid()
        assert "password1" in form.errors

    def test_password_requires_alpha(self):
        """Password must contain at least one letter."""
        form = SignUpForm(
            data={
                "username": "TestUser",
                "password1": "12345@",
                "password2": "12345@",
            }
        )
        assert not form.is_valid()
        assert "password1" in form.errors
        assert "letter" in str(form.errors["password1"]).lower()

    def test_password_requires_digit(self):
        """Password must contain at least one digit."""
        form = SignUpForm(
            data={
                "username": "TestUser",
                "password1": "abcde@",
                "password2": "abcde@",
            }
        )
        assert not form.is_valid()
        assert "password1" in form.errors
        assert "digit" in str(form.errors["password1"]).lower()

    def test_password_requires_special_char(self):
        """Password must contain one of: $, %, *, @."""
        form = SignUpForm(
            data={
                "username": "TestUser",
                "password1": "test12",
                "password2": "test12",
            }
        )
        assert not form.is_valid()
        assert "password1" in form.errors

    def test_password_accepts_dollar_sign(self):
        """Password with $ should be valid."""
        form = SignUpForm(
            data={
                "username": "TestUser",
                "password1": "test1$",
                "password2": "test1$",
            }
        )
        assert form.is_valid()

    def test_password_accepts_percent(self):
        """Password with % should be valid."""
        form = SignUpForm(
            data={
                "username": "TestUser",
                "password1": "test1%",
                "password2": "test1%",
            }
        )
        assert form.is_valid()

    def test_password_accepts_asterisk(self):
        """Password with * should be valid."""
        form = SignUpForm(
            data={
                "username": "TestUser",
                "password1": "test1*",
                "password2": "test1*",
            }
        )
        assert form.is_valid()

    def test_password_accepts_at_sign(self):
        """Password with @ should be valid."""
        form = SignUpForm(
            data={
                "username": "TestUser",
                "password1": "test1@",
                "password2": "test1@",
            }
        )
        assert form.is_valid()

    def test_password_mismatch(self):
        """Password confirmation must match."""
        form = SignUpForm(
            data={
                "username": "TestUser",
                "password1": "test1@",
                "password2": "test2@",
            }
        )
        assert not form.is_valid()
        assert "password2" in form.errors


@pytest.mark.django_db
class TestGuessValidation:
    """Test guess input validation."""

    def test_guess_uppercase_conversion(self):
        """Guesses should be converted to uppercase."""
        from game.forms import GuessForm

        form = GuessForm(data={"guess": "apple"})
        assert form.is_valid()
        assert form.cleaned_data["guess"] == "APPLE"

    def test_guess_exact_length(self):
        """Guess must be exactly 5 letters."""
        from game.forms import GuessForm

        form = GuessForm(data={"guess": "app"})
        assert not form.is_valid()

        form = GuessForm(data={"guess": "apples"})
        assert not form.is_valid()

    def test_guess_only_letters(self):
        """Guess must contain only letters."""
        from game.forms import GuessForm

        form = GuessForm(data={"guess": "app1e"})
        assert not form.is_valid()

        form = GuessForm(data={"guess": "app@e"})
        assert not form.is_valid()

    def test_valid_guess(self):
        """Valid 5-letter guess."""
        from game.forms import GuessForm

        form = GuessForm(data={"guess": "apple"})
        assert form.is_valid()

