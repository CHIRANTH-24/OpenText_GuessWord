"""Custom authentication forms with validation rules."""
import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class SignUpForm(UserCreationForm):
    """
    Custom registration form with specific validation rules:
    - Username: ≥5 letters, must include both upper and lower case letters
    - Password: ≥5 characters, must include at least one alpha, one digit,
                and one special character from {$, %, *, @}
    """

    username = forms.CharField(
        max_length=150,
        min_length=5,
        help_text="At least 5 letters with both uppercase and lowercase.",
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        min_length=5,
        help_text="At least 5 characters including one letter, one digit, and one of: $ % * @",
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text="Enter the same password as before, for verification.",
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def clean_username(self):
        """Validate username according to requirements."""
        username = self.cleaned_data.get("username")

        if not username:
            raise ValidationError("Username is required.")

        # Check minimum length
        if len(username) < 5:
            raise ValidationError("Username must be at least 5 characters long.")

        # Check for at least one uppercase letter
        if not any(c.isupper() for c in username):
            raise ValidationError("Username must contain at least one uppercase letter.")

        # Check for at least one lowercase letter
        if not any(c.islower() for c in username):
            raise ValidationError("Username must contain at least one lowercase letter.")

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")

        return username

    def clean_password1(self):
        """Validate password according to requirements."""
        password = self.cleaned_data.get("password1")

        if not password:
            raise ValidationError("Password is required.")

        # Check minimum length
        if len(password) < 5:
            raise ValidationError("Password must be at least 5 characters long.")

        # Check for at least one alphabetic character
        if not any(c.isalpha() for c in password):
            raise ValidationError("Password must contain at least one letter.")

        # Check for at least one digit
        if not any(c.isdigit() for c in password):
            raise ValidationError("Password must contain at least one digit.")

        # Check for at least one special character from the required set
        special_chars = {"$", "%", "*", "@"}
        if not any(c in special_chars for c in password):
            raise ValidationError("Password must contain at least one of: $ % * @")

        return password

    def clean_password2(self):
        """Validate that password2 matches password1."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields didn't match.")

        return password2

