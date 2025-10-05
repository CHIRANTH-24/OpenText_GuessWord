"""Views for the game app."""
import csv
from datetime import datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import GuessForm
from .models import DailyQuota, Game, Guess, Word
from .utils import compute_guess_colors


def home(request):
    """Landing page."""
    context = {}
    if request.user.is_authenticated:
        today = timezone.localdate()
        quota, _ = DailyQuota.objects.get_or_create(user=request.user, date=today)
        context["games_played_today"] = quota.words_started_count
        context["games_remaining"] = max(0, 3 - quota.words_started_count)

        # Get active game if any
        active_game = (
            Game.objects.filter(user=request.user, finished_at__isnull=True)
            .order_by("-started_at")
            .first()
        )
        context["active_game"] = active_game

    return render(request, "game/home.html", context)


@login_required
@transaction.atomic
def start_game(request):
    """Start a new game for the logged-in user."""
    if request.method != "POST":
        return redirect("home")

    today = timezone.localdate()

    # Get or create daily quota
    quota, _ = DailyQuota.objects.select_for_update().get_or_create(
        user=request.user, date=today
    )

    # Check if user has exceeded daily limit
    if quota.words_started_count >= 3:
        messages.error(
            request, "You've reached your daily limit of 3 games. Come back tomorrow!"
        )
        return redirect("home")

    # Check if there's already an unfinished game
    active_game = Game.objects.filter(user=request.user, finished_at__isnull=True).first()
    if active_game:
        messages.info(request, "You have an active game. Finish it before starting a new one.")
        return redirect("game_detail", game_id=active_game.id)

    # Select a random word
    words = list(Word.objects.all())
    if not words:
        messages.error(request, "No words available. Please contact the administrator.")
        return redirect("home")

    import random

    target_word = random.choice(words)

    # Create the game
    game = Game.objects.create(user=request.user, target_word=target_word)

    # Increment quota
    quota.words_started_count += 1
    quota.save()

    messages.success(request, "New game started! You have 5 guesses.")
    return redirect("game_detail", game_id=game.id)


@login_required
def game_detail(request, game_id):
    """Display the game board and handle game state."""
    game = get_object_or_404(Game, id=game_id, user=request.user)

    # Get all guesses with their colors
    guesses = game.guesses.order_by("index")
    guess_data = []

    for guess in guesses:
        colors = compute_guess_colors(guess.text, game.target_word.text)
        guess_data.append({"text": guess.text, "colors": colors, "index": guess.index})

    # Create empty rows for remaining guesses
    remaining_rows = max(0, 5 - len(guess_data))

    context = {
        "game": game,
        "guess_data": guess_data,
        "remaining_rows": remaining_rows,
        "form": GuessForm() if game.can_guess else None,
        "guesses_remaining": 5 - game.guesses_count,
    }

    return render(request, "game/board.html", context)


@login_required
@transaction.atomic
def submit_guess(request, game_id):
    """Handle guess submission via HTMX."""
    game = get_object_or_404(Game.objects.select_for_update(), id=game_id, user=request.user)

    if not game.can_guess:
        messages.error(request, "This game is already finished or you've used all your guesses.")
        return render_board_partial(request, game)

    if request.method != "POST":
        return render_board_partial(request, game)

    form = GuessForm(request.POST)

    if not form.is_valid():
        for error in form.errors.get("guess", []):
            messages.error(request, error)
        return render_board_partial(request, game)

    guess_text = form.cleaned_data["guess"]
    guess_index = game.guesses_count + 1

    # Create the guess
    Guess.objects.create(game=game, text=guess_text, index=guess_index)

    # Check if guess is correct
    if guess_text == game.target_word.text:
        game.won = True
        game.finished_at = timezone.now()
        game.save()
        messages.success(request, f"🎉 Congratulations! You guessed it: {game.target_word.text}")
    elif guess_index >= 5:
        # Game over - used all 5 guesses
        game.finished_at = timezone.now()
        game.won = False
        game.save()
        messages.info(
            request,
            f"Better luck next time! The word was: {game.target_word.text}",
        )
    else:
        guesses_left = 5 - guess_index
        messages.info(request, f"Not quite! You have {guesses_left} guess(es) remaining.")

    return render_board_partial(request, game)


def render_board_partial(request, game):
    """Render just the board partial for HTMX updates."""
    guesses = game.guesses.order_by("index")
    guess_data = []

    for guess in guesses:
        colors = compute_guess_colors(guess.text, game.target_word.text)
        guess_data.append({"text": guess.text, "colors": colors, "index": guess.index})

    remaining_rows = max(0, 5 - len(guess_data))

    context = {
        "game": game,
        "guess_data": guess_data,
        "remaining_rows": remaining_rows,
        "form": GuessForm() if game.can_guess else None,
        "guesses_remaining": 5 - game.guesses_count,
    }

    return render(request, "game/_board_partial.html", context)


@staff_member_required
def daily_report(request):
    """Display daily report of games played."""
    date_str = request.GET.get("date")
    export = request.GET.get("export") == "csv"

    if date_str:
        try:
            report_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
            report_date = timezone.localdate()
    else:
        report_date = timezone.localdate()

    # Get games for the specified date
    games = Game.objects.filter(started_at__date=report_date)

    # Calculate statistics
    distinct_users = games.values("user").distinct().count()
    won_games = games.filter(won=True).count()
    total_games = games.count()

    if export:
        # Export as CSV
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="daily_report_{report_date}.csv"'

        writer = csv.writer(response)
        writer.writerow(["Date", "Distinct Users", "Games Played", "Games Won"])
        writer.writerow([report_date, distinct_users, total_games, won_games])

        return response

    context = {
        "report_date": report_date,
        "distinct_users": distinct_users,
        "won_games": won_games,
        "total_games": total_games,
    }

    return render(request, "game/daily_report.html", context)


@staff_member_required
def user_report(request):
    """Display per-user report of games played."""
    username = request.GET.get("username")
    export = request.GET.get("export") == "csv"

    if not username:
        # Show form to select user
        from django.contrib.auth.models import User

        users = User.objects.filter(games__isnull=False).distinct().order_by("username")
        return render(request, "game/user_report.html", {"users": users})

    from django.contrib.auth.models import User

    user = get_object_or_404(User, username=username)

    # Aggregate games by date
    games_by_date = (
        Game.objects.filter(user=user)
        .extra(select={"date": "DATE(started_at)"})
        .values("date")
        .annotate(words_tried=Count("id"), correct_guesses=Count("id", filter=Q(won=True)))
        .order_by("-date")
    )

    if export:
        # Export as CSV
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="user_report_{username}.csv"'

        writer = csv.writer(response)
        writer.writerow(["Date", "Words Tried", "Correct Guesses"])

        for entry in games_by_date:
            writer.writerow([entry["date"], entry["words_tried"], entry["correct_guesses"]])

        return response

    context = {"report_user": user, "games_by_date": games_by_date}

    return render(request, "game/user_report.html", context)

