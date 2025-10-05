"""Utility functions for game logic."""
from typing import List, Tuple


def compute_guess_colors(guess: str, target: str) -> List[Tuple[str, str]]:
    """
    Compute the color for each letter in the guess.

    Returns a list of tuples: [(letter, color), ...]
    where color is 'green', 'orange', or 'grey'.

    Algorithm (handles duplicates correctly):
    1. First pass: mark exact matches (green) and build frequency map of remaining letters
    2. Second pass: mark letters in wrong position (orange) using frequency map
    3. Everything else is grey
    """
    guess = guess.upper()
    target = target.upper()

    result = [("", "")] * 5  # Initialize result list
    target_freq = {}

    # Build frequency map of target letters
    for char in target:
        target_freq[char] = target_freq.get(char, 0) + 1

    # First pass: mark greens and decrement frequency
    for i in range(5):
        if guess[i] == target[i]:
            result[i] = (guess[i], "green")
            target_freq[guess[i]] -= 1

    # Second pass: mark oranges and greys
    for i in range(5):
        if result[i][1] == "green":
            # Already marked as green
            continue

        letter = guess[i]
        if letter in target_freq and target_freq[letter] > 0:
            result[i] = (letter, "orange")
            target_freq[letter] -= 1
        else:
            result[i] = (letter, "grey")

    return result

