"""URL configuration for game app."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("game/start/", views.start_game, name="start_game"),
    path("game/<int:game_id>/", views.game_detail, name="game_detail"),
    path("game/<int:game_id>/guess/", views.submit_guess, name="submit_guess"),
    path("reports/daily/", views.daily_report, name="daily_report"),
    path("reports/user/", views.user_report, name="user_report"),
]

