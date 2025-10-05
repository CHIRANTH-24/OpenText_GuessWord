"""Models for the Wordle-style game."""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


def validate_uppercase_5letter(value):
    """Validate that the value is exactly 5 uppercase letters."""
    if len(value) != 5:
        raise ValidationError("Must be exactly 5 characters long.")
    if not value.isupper():
        raise ValidationError("Must be uppercase.")
    if not value.isalpha():
        raise ValidationError("Must contain only letters.")


class Word(models.Model):
    """A 5-letter word that can be used as a target in the game."""

    text = models.CharField(
        max_length=5, unique=True, validators=[validate_uppercase_5letter]
    )

    class Meta:
        ordering = ["text"]

    def __str__(self):
        return self.text

    def clean(self):
        """Ensure text is uppercase before validation."""
        if self.text:
            self.text = self.text.upper()
        super().clean()

    def save(self, *args, **kwargs):
        """Ensure text is uppercase before saving."""
        self.full_clean()
        super().save(*args, **kwargs)


class Game(models.Model):
    """A single game session for a user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")
    target_word = models.ForeignKey(Word, on_delete=models.PROTECT, related_name="games")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    won = models.BooleanField(default=False)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["user", "-started_at"]),
            models.Index(fields=["started_at"]),
        ]

    def __str__(self):
        status = "Won" if self.won else "Lost" if self.finished_at else "In Progress"
        return f"Game {self.id} - {self.user.username} - {status}"

    @property
    def is_finished(self):
        """Check if the game is finished."""
        return self.finished_at is not None

    @property
    def guesses_count(self):
        """Count of guesses made in this game."""
        return self.guesses.count()

    @property
    def can_guess(self):
        """Check if the player can make another guess."""
        return not self.is_finished and self.guesses_count < 5


class Guess(models.Model):
    """A single guess in a game."""

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="guesses")
    text = models.CharField(max_length=5, validators=[validate_uppercase_5letter])
    index = models.PositiveSmallIntegerField()  # 1-5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["game", "index"]
        unique_together = [["game", "index"]]
        indexes = [
            models.Index(fields=["game", "index"]),
        ]

    def __str__(self):
        return f"Guess {self.index} - {self.text} (Game {self.game_id})"

    def clean(self):
        """Ensure text is uppercase and index is valid."""
        if self.text:
            self.text = self.text.upper()
        if self.index and (self.index < 1 or self.index > 5):
            raise ValidationError("Index must be between 1 and 5.")
        super().clean()

    def save(self, *args, **kwargs):
        """Ensure text is uppercase before saving."""
        self.full_clean()
        super().save(*args, **kwargs)


class DailyQuota(models.Model):
    """Tracks the number of games started by a user on a specific date."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_quotas")
    date = models.DateField()
    words_started_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = [["user", "date"]]
        indexes = [
            models.Index(fields=["user", "date"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.words_started_count}/3"

