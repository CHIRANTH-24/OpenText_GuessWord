"""Tests for admin reports functionality."""
import csv
from io import StringIO

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from game.models import Game, Word


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_superuser(
        username="AdminUser", password="admin1@", email="admin@test.com"
    )


@pytest.fixture
def regular_user(db):
    """Create a regular user."""
    return User.objects.create_user(username="UserOne", password="test1@")


@pytest.fixture
def word(db):
    """Create a test word."""
    return Word.objects.create(text="APPLE")


@pytest.mark.django_db
class TestDailyReport:
    """Test daily report functionality."""

    def test_daily_report_requires_staff(self, client, regular_user):
        """Regular users cannot access daily report."""
        client.force_login(regular_user)
        response = client.get(reverse("daily_report"))
        assert response.status_code == 302

    def test_daily_report_accessible_by_admin(self, client, admin_user):
        """Admin users can access daily report."""
        client.force_login(admin_user)
        response = client.get(reverse("daily_report"))
        assert response.status_code == 200

    def test_daily_report_counts_distinct_users(self, client, admin_user, word):
        """Daily report correctly counts distinct users."""
        # Create games for different users
        user1 = User.objects.create_user(username="User1One", password="test1@")
        user2 = User.objects.create_user(username="User2Two", password="test1@")

        today = timezone.now()
        Game.objects.create(user=user1, target_word=word, started_at=today)
        Game.objects.create(user=user1, target_word=word, started_at=today)
        Game.objects.create(user=user2, target_word=word, started_at=today)

        client.force_login(admin_user)
        response = client.get(
            reverse("daily_report"), {"date": today.strftime("%Y-%m-%d")}
        )

        assert response.status_code == 200
        assert response.context["distinct_users"] == 2

    def test_daily_report_counts_won_games(self, client, admin_user, word):
        """Daily report correctly counts won games."""
        user = User.objects.create_user(username="UserOne", password="test1@")
        today = timezone.now()

        # Create won and lost games
        Game.objects.create(
            user=user,
            target_word=word,
            started_at=today,
            finished_at=today,
            won=True,
        )
        Game.objects.create(
            user=user,
            target_word=word,
            started_at=today,
            finished_at=today,
            won=False,
        )
        Game.objects.create(
            user=user,
            target_word=word,
            started_at=today,
            finished_at=today,
            won=True,
        )

        client.force_login(admin_user)
        response = client.get(
            reverse("daily_report"), {"date": today.strftime("%Y-%m-%d")}
        )

        assert response.status_code == 200
        assert response.context["won_games"] == 2
        assert response.context["total_games"] == 3

    def test_daily_report_csv_export(self, client, admin_user, word):
        """Daily report can be exported as CSV."""
        user = User.objects.create_user(username="UserOne", password="test1@")
        today = timezone.now()

        Game.objects.create(
            user=user,
            target_word=word,
            started_at=today,
            finished_at=today,
            won=True,
        )

        client.force_login(admin_user)
        response = client.get(
            reverse("daily_report"),
            {"date": today.strftime("%Y-%m-%d"), "export": "csv"},
        )

        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"
        assert "daily_report" in response["Content-Disposition"]

        # Parse CSV content
        content = response.content.decode("utf-8")
        csv_reader = csv.reader(StringIO(content))
        rows = list(csv_reader)

        assert len(rows) == 2  # Header + data row
        assert rows[0] == ["Date", "Distinct Users", "Games Played", "Games Won"]


@pytest.mark.django_db
class TestUserReport:
    """Test per-user report functionality."""

    def test_user_report_requires_staff(self, client, regular_user):
        """Regular users cannot access user report."""
        client.force_login(regular_user)
        response = client.get(reverse("user_report"))
        assert response.status_code == 302

    def test_user_report_accessible_by_admin(self, client, admin_user):
        """Admin users can access user report."""
        client.force_login(admin_user)
        response = client.get(reverse("user_report"))
        assert response.status_code == 200

    def test_user_report_shows_user_selector(self, client, admin_user, word):
        """User report shows user selection form."""
        # Create a user with games
        user = User.objects.create_user(username="UserOne", password="test1@")
        Game.objects.create(user=user, target_word=word)

        client.force_login(admin_user)
        response = client.get(reverse("user_report"))

        assert response.status_code == 200
        assert "users" in response.context

    def test_user_report_aggregates_by_date(self, client, admin_user, word):
        """User report aggregates games by date."""
        user = User.objects.create_user(username="UserOne", password="test1@")
        today = timezone.now()
        yesterday = today - timezone.timedelta(days=1)

        # Create games on different days
        Game.objects.create(
            user=user,
            target_word=word,
            started_at=today,
            finished_at=today,
            won=True,
        )
        Game.objects.create(
            user=user,
            target_word=word,
            started_at=today,
            finished_at=today,
            won=False,
        )
        Game.objects.create(
            user=user,
            target_word=word,
            started_at=yesterday,
            finished_at=yesterday,
            won=True,
        )

        client.force_login(admin_user)
        response = client.get(reverse("user_report"), {"username": user.username})

        assert response.status_code == 200
        games_by_date = response.context["games_by_date"]
        assert len(games_by_date) == 2

    def test_user_report_csv_export(self, client, admin_user, word):
        """User report can be exported as CSV."""
        user = User.objects.create_user(username="UserOne", password="test1@")
        today = timezone.now()

        Game.objects.create(
            user=user,
            target_word=word,
            started_at=today,
            finished_at=today,
            won=True,
        )
        Game.objects.create(
            user=user,
            target_word=word,
            started_at=today,
            finished_at=today,
            won=False,
        )

        client.force_login(admin_user)
        response = client.get(
            reverse("user_report"), {"username": user.username, "export": "csv"}
        )

        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"
        assert f"user_report_{user.username}" in response["Content-Disposition"]

        # Parse CSV content
        content = response.content.decode("utf-8")
        csv_reader = csv.reader(StringIO(content))
        rows = list(csv_reader)

        assert len(rows) == 2  # Header + data row
        assert rows[0] == ["Date", "Words Tried", "Correct Guesses"]
        assert rows[1][1] == "2"  # 2 words tried
        assert rows[1][2] == "1"  # 1 correct

