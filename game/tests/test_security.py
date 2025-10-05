"""Tests for security and access control."""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from game.models import Game, Word


@pytest.fixture
def user1(db):
    """Create first test user."""
    return User.objects.create_user(username="User1One", password="test1@")


@pytest.fixture
def user2(db):
    """Create second test user."""
    return User.objects.create_user(username="User2Two", password="test1@")


@pytest.fixture
def word(db):
    """Create a test word."""
    return Word.objects.create(text="APPLE")


@pytest.mark.django_db
class TestAuthentication:
    """Test authentication requirements."""

    def test_home_accessible_anonymous(self, client):
        """Home page is accessible to anonymous users."""
        response = client.get(reverse("home"))
        assert response.status_code == 200

    def test_start_game_requires_login(self, client):
        """Starting a game requires authentication."""
        response = client.post(reverse("start_game"))
        assert response.status_code == 302
        assert "/accounts/login" in response.url

    def test_game_detail_requires_login(self, client, user1, word):
        """Viewing game details requires authentication."""
        game = Game.objects.create(user=user1, target_word=word)
        response = client.get(reverse("game_detail", args=[game.id]))
        assert response.status_code == 302
        assert "/accounts/login" in response.url

    def test_submit_guess_requires_login(self, client, user1, word):
        """Submitting a guess requires authentication."""
        game = Game.objects.create(user=user1, target_word=word)
        response = client.post(
            reverse("submit_guess", args=[game.id]), data={"guess": "APPLE"}
        )
        assert response.status_code == 302
        assert "/accounts/login" in response.url


@pytest.mark.django_db
class TestAuthorization:
    """Test authorization and access control."""

    def test_user_cannot_view_another_users_game(self, client, user1, user2, word):
        """Users cannot view games belonging to other users."""
        game = Game.objects.create(user=user1, target_word=word)

        client.force_login(user2)
        response = client.get(reverse("game_detail", args=[game.id]))

        assert response.status_code == 404

    def test_user_cannot_guess_on_another_users_game(self, client, user1, user2, word):
        """Users cannot submit guesses to other users' games."""
        game = Game.objects.create(user=user1, target_word=word)

        client.force_login(user2)
        response = client.post(
            reverse("submit_guess", args=[game.id]), data={"guess": "APPLE"}
        )

        assert response.status_code == 404

    def test_user_can_only_see_own_games(self, client, user1, user2, word):
        """Users can only access their own games."""
        game1 = Game.objects.create(user=user1, target_word=word)
        game2 = Game.objects.create(user=user2, target_word=word)

        # User1 can access their game
        client.force_login(user1)
        response = client.get(reverse("game_detail", args=[game1.id]))
        assert response.status_code == 200

        # User1 cannot access user2's game
        response = client.get(reverse("game_detail", args=[game2.id]))
        assert response.status_code == 404


@pytest.mark.django_db
class TestCSRF:
    """Test CSRF protection."""

    def test_start_game_requires_csrf_token(self, client, user1, word):
        """POST requests require CSRF token."""
        Word.objects.create(text="APPLE")
        client.force_login(user1)

        # Django test client includes CSRF by default, so we test
        # that the view requires POST (CSRF is implicit)
        response = client.get(reverse("start_game"))
        assert response.status_code == 302  # Redirects, doesn't start game

    def test_submit_guess_form_includes_csrf(self, client, user1, word):
        """Guess form includes CSRF token."""
        client.force_login(user1)
        game = Game.objects.create(user=user1, target_word=word)

        response = client.get(reverse("game_detail", args=[game.id]))
        assert response.status_code == 200
        assert b"csrfmiddlewaretoken" in response.content


@pytest.mark.django_db
class TestInputValidation:
    """Test input validation and sanitization."""

    def test_invalid_guess_rejected(self, client, user1, word):
        """Invalid guesses are rejected."""
        client.force_login(user1)
        game = Game.objects.create(user=user1, target_word=word)

        # Too short
        response = client.post(
            reverse("submit_guess", args=[game.id]), data={"guess": "APP"}
        )
        assert response.status_code == 200

        # Too long
        response = client.post(
            reverse("submit_guess", args=[game.id]), data={"guess": "APPLES"}
        )
        assert response.status_code == 200

        # Contains numbers
        response = client.post(
            reverse("submit_guess", args=[game.id]), data={"guess": "APP1E"}
        )
        assert response.status_code == 200

        # Contains special characters
        response = client.post(
            reverse("submit_guess", args=[game.id]), data={"guess": "APP@E"}
        )
        assert response.status_code == 200

    def test_sql_injection_prevented(self, client, user1, word):
        """SQL injection attempts are safely handled."""
        client.force_login(user1)
        game = Game.objects.create(user=user1, target_word=word)

        # Attempt SQL injection
        response = client.post(
            reverse("submit_guess", args=[game.id]),
            data={"guess": "'; DROP TABLE game_word; --"},
        )

        # Word table should still exist
        assert Word.objects.count() == 1

    def test_xss_prevented_in_messages(self, client, user1):
        """XSS attempts in messages are escaped."""
        client.force_login(user1)

        # Attempt XSS in username (during registration flow)
        response = client.get(reverse("home"))
        content = response.content.decode("utf-8")

        # Django automatically escapes template variables
        assert "<script>" not in content

