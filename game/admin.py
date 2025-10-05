"""Admin configuration for game app."""
import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from .models import DailyQuota, Game, Guess, Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    """Admin interface for Word model."""

    list_display = ["text", "games_count"]
    search_fields = ["text"]
    ordering = ["text"]

    def games_count(self, obj):
        """Count of games using this word."""
        return obj.games.count()

    games_count.short_description = "Games Count"


class GuessInline(admin.TabularInline):
    """Inline display of guesses for a game."""

    model = Guess
    extra = 0
    readonly_fields = ["text", "index", "created_at"]
    can_delete = False
    ordering = ["index"]


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Admin interface for Game model."""

    list_display = [
        "id",
        "user",
        "target_word",
        "started_at",
        "status_display",
        "guesses_count",
    ]
    list_filter = ["won", "started_at", "finished_at"]
    search_fields = ["user__username", "target_word__text"]
    readonly_fields = ["started_at", "finished_at", "guesses_count"]
    date_hierarchy = "started_at"
    inlines = [GuessInline]
    actions = ["export_as_csv"]

    def status_display(self, obj):
        """Display game status with color."""
        if obj.finished_at is None:
            return format_html('<span style="color: blue;">In Progress</span>')
        elif obj.won:
            return format_html('<span style="color: green;">Won</span>')
        else:
            return format_html('<span style="color: red;">Lost</span>')

    status_display.short_description = "Status"

    def export_as_csv(self, request, queryset):
        """Export selected games as CSV."""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="games_export.csv"'

        writer = csv.writer(response)
        writer.writerow(
            ["ID", "User", "Target Word", "Started At", "Finished At", "Won", "Guesses"]
        )

        for game in queryset:
            writer.writerow(
                [
                    game.id,
                    game.user.username,
                    game.target_word.text,
                    game.started_at,
                    game.finished_at or "",
                    "Yes" if game.won else "No",
                    game.guesses_count,
                ]
            )

        return response

    export_as_csv.short_description = "Export selected games as CSV"


@admin.register(Guess)
class GuessAdmin(admin.ModelAdmin):
    """Admin interface for Guess model."""

    list_display = ["id", "game", "text", "index", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["text", "game__user__username"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"


@admin.register(DailyQuota)
class DailyQuotaAdmin(admin.ModelAdmin):
    """Admin interface for DailyQuota model."""

    list_display = ["user", "date", "words_started_count", "quota_status"]
    list_filter = ["date"]
    search_fields = ["user__username"]
    date_hierarchy = "date"

    def quota_status(self, obj):
        """Display quota status."""
        if obj.words_started_count >= 3:
            return format_html('<span style="color: red;">Limit Reached</span>')
        else:
            return format_html(
                '<span style="color: green;">{}/3</span>', obj.words_started_count
            )

    quota_status.short_description = "Quota Status"

