"""Forms for the game app."""
from django import forms
from django.core.exceptions import ValidationError


class GuessForm(forms.Form):
    """Form for submitting a guess."""

    guess = forms.CharField(
        max_length=5,
        min_length=5,
        widget=forms.TextInput(
            attrs={
                "class": "guess-input",
                "placeholder": "Enter 5 letters",
                "maxlength": "5",
                "pattern": "[A-Za-z]{5}",
                "autocomplete": "off",
                "autofocus": True,
            }
        ),
    )

    def clean_guess(self):
        """Validate and normalize the guess."""
        guess = self.cleaned_data.get("guess", "")

        # Convert to uppercase
        guess = guess.upper()

        # Validate length
        if len(guess) != 5:
            raise ValidationError("Guess must be exactly 5 letters.")

        # Validate only letters
        if not guess.isalpha():
            raise ValidationError("Guess must contain only letters.")

        return guess

