"""Tests for game flow and mechanics."""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from game.models import DailyQuota, Game, Guess, Word


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(username="TestUser", password="test1@")


@pytest.fixture
def words(db):
    """Create test words."""
    return [
        Word.objects.create(text="APPLE"),
        Word.objects.create(text="BRAVE"),
        Word.objects.create(text="CLOUD"),
    ]


@pytest.mark.django_db
class TestGameCreation:
    """Test game creation and initialization."""

    def test_start_game_creates_game(self, client, user, words):
        """Starting a game creates a Game instance."""
        client.force_login(user)
        response = client.post(reverse("start_game"))

        assert Game.objects.filter(user=user).count() == 1
        game = Game.objects.get(user=user)
        assert game.target_word in words
        assert game.finished_at is None
        assert not game.won

    def test_start_game_increments_quota(self, client, user, words):
        """Starting a game increments daily quota."""
        client.force_login(user)
        today = timezone.localdate()

        client.post(reverse("start_game"))

        quota = DailyQuota.objects.get(user=user, date=today)
        assert quota.words_started_count == 1

    def test_start_game_requires_authentication(self, client, words):
        """Anonymous users cannot start a game."""
        response = client.post(reverse("start_game"))
        assert response.status_code == 302
        assert "/accounts/login" in response.url


@pytest.mark.django_db
class TestGameGuessing:
    """Test guess submission and validation."""

    def test_submit_valid_guess(self, client, user, words):
        """Submitting a valid guess creates a Guess instance."""
        client.force_login(user)
        client.post(reverse("start_game"))
        game = Game.objects.get(user=user)

        response = client.post(
            reverse("submit_guess", args=[game.id]), data={"guess": "APPLE"}
        )

        assert response.status_code == 200
        assert Guess.objects.filter(game=game).count() == 1
        guess = Guess.objects.get(game=game)
        assert guess.text == "APPLE"
        assert guess.index == 1

    def test_submit_lowercase_guess(self, client, user, words):
        """Lowercase guesses are converted to uppercase."""
        client.force_login(user)
        client.post(reverse("start_game"))
        game = Game.objects.get(user=user)

        client.post(reverse("submit_guess", args=[game.id]), data={"guess": "apple"})

        guess = Guess.objects.get(game=game)
        assert guess.text == "APPLE"

    def test_correct_guess_wins_game(self, client, user):
        """Guessing the correct word marks game as won."""
        Word.objects.create(text="APPLE")
        client.force_login(user)

        # Create game with known target
        game = Game.objects.create(
            user=user, target_word=Word.objects.get(text="APPLE")
        )

        client.post(reverse("submit_guess", args=[game.id]), data={"guess": "APPLE"})

        game.refresh_from_db()
        assert game.won
        assert game.finished_at is not None

    def test_five_wrong_guesses_loses_game(self, client, user):
        """Five wrong guesses marks game as lost."""
        Word.objects.create(text="APPLE")
        Word.objects.create(text="WRONG")
        client.force_login(user)

        game = Game.objects.create(
            user=user, target_word=Word.objects.get(text="APPLE")
        )

        # Submit 5 wrong guesses
        for i in range(5):
            client.post(
                reverse("submit_guess", args=[game.id]), data={"guess": "WRONG"}
            )

        game.refresh_from_db()
        assert not game.won
        assert game.finished_at is not None
        assert Guess.objects.filter(game=game).count() == 5

    def test_cannot_guess_after_game_finished(self, client, user):
        """Cannot submit guesses after game is finished."""
        Word.objects.create(text="APPLE")
        client.force_login(user)

        game = Game.objects.create(
            user=user, target_word=Word.objects.get(text="APPLE")
        )
        game.finished_at = timezone.now()
        game.save()

        response = client.post(
            reverse("submit_guess", args=[game.id]), data={"guess": "BRAVE"}
        )

        assert Guess.objects.filter(game=game).count() == 0

    def test_guesses_ordered_correctly(self, client, user, words):
        """Guesses are saved with correct order."""
        client.force_login(user)
        client.post(reverse("start_game"))
        game = Game.objects.get(user=user)

        guesses = ["APPLE", "BRAVE", "CLOUD"]
        for guess_text in guesses:
            client.post(
                reverse("submit_guess", args=[game.id]), data={"guess": guess_text}
            )

        saved_guesses = list(Guess.objects.filter(game=game).order_by("index"))
        assert len(saved_guesses) == 3
        assert saved_guesses[0].text == "APPLE"
        assert saved_guesses[0].index == 1
        assert saved_guesses[1].text == "BRAVE"
        assert saved_guesses[1].index == 2
        assert saved_guesses[2].text == "CLOUD"
        assert saved_guesses[2].index == 3

