"""Tests for daily quota enforcement."""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from game.models import DailyQuota, Game, Word


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
        Word.objects.create(text="DELTA"),
    ]


@pytest.mark.django_db
class TestDailyQuota:
    """Test daily game limit enforcement."""

    def test_can_start_three_games_per_day(self, client, user, words):
        """User can start up to 3 games per day."""
        client.force_login(user)
        today = timezone.localdate()

        # Start 3 games
        for i in range(3):
            response = client.post(reverse("start_game"), follow=True)
            assert response.status_code == 200

            # Finish the game to allow starting a new one
            game = Game.objects.filter(user=user, finished_at__isnull=True).first()
            if game:
                game.finished_at = timezone.now()
                game.save()

        quota = DailyQuota.objects.get(user=user, date=today)
        assert quota.words_started_count == 3

    def test_cannot_start_fourth_game_same_day(self, client, user, words):
        """User cannot start a 4th game on the same day."""
        client.force_login(user)
        today = timezone.localdate()

        # Create quota at limit
        DailyQuota.objects.create(user=user, date=today, words_started_count=3)

        response = client.post(reverse("start_game"), follow=True)

        # Should redirect back to home with error message
        assert "daily limit" in str(response.content).lower()
        assert Game.objects.filter(user=user).count() == 0

    def test_quota_resets_new_day(self, client, user, words):
        """Quota should be independent per day."""
        client.force_login(user)
        today = timezone.localdate()
        yesterday = today - timezone.timedelta(days=1)

        # Create quota for yesterday at limit
        DailyQuota.objects.create(user=user, date=yesterday, words_started_count=3)

        # Should be able to start game today
        response = client.post(reverse("start_game"))
        assert response.status_code == 302

        # Check today's quota
        today_quota = DailyQuota.objects.get(user=user, date=today)
        assert today_quota.words_started_count == 1

    def test_multiple_users_independent_quotas(self, client, words):
        """Different users have independent quotas."""
        user1 = User.objects.create_user(username="User1One", password="test1@")
        user2 = User.objects.create_user(username="User2Two", password="test1@")
        today = timezone.localdate()

        # User1 uses all 3 games
        DailyQuota.objects.create(user=user1, date=today, words_started_count=3)

        # User2 should still be able to start games
        client.force_login(user2)
        response = client.post(reverse("start_game"))
        assert response.status_code == 302

        user2_quota = DailyQuota.objects.get(user=user2, date=today)
        assert user2_quota.words_started_count == 1

    def test_quota_increments_atomically(self, client, user, words):
        """Quota increments are atomic (transaction-safe)."""
        client.force_login(user)

        # Start game
        client.post(reverse("start_game"))

        # Finish game
        game = Game.objects.get(user=user)
        game.finished_at = timezone.now()
        game.save()

        # Start another game
        client.post(reverse("start_game"))

        # Check quota
        today = timezone.localdate()
        quota = DailyQuota.objects.get(user=user, date=today)
        assert quota.words_started_count == 2

    def test_cannot_start_game_with_active_game(self, client, user, words):
        """Cannot start a new game while one is active."""
        client.force_login(user)

        # Start first game
        client.post(reverse("start_game"))

        # Try to start second game without finishing first
        response = client.post(reverse("start_game"), follow=True)

        # Should redirect with info message
        assert "active game" in str(response.content).lower()
        assert Game.objects.filter(user=user).count() == 1

    def test_can_start_new_game_after_finishing(self, client, user, words):
        """Can start a new game after finishing the current one."""
        client.force_login(user)

        # Start and finish first game
        client.post(reverse("start_game"))
        game = Game.objects.get(user=user)
        game.finished_at = timezone.now()
        game.save()

        # Start second game
        response = client.post(reverse("start_game"))
        assert response.status_code == 302

        # Should have 2 games total
        assert Game.objects.filter(user=user).count() == 2

