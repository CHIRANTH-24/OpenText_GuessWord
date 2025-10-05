"""Tests for the guess coloring logic."""
import pytest

from game.utils import compute_guess_colors


class TestColoringLogic:
    """Test the coloring algorithm for guess feedback."""

    def test_all_correct(self):
        """All letters correct and in right position."""
        result = compute_guess_colors("APPLE", "APPLE")
        expected = [
            ("A", "green"),
            ("P", "green"),
            ("P", "green"),
            ("L", "green"),
            ("E", "green"),
        ]
        assert result == expected

    def test_all_wrong(self):
        """No letters match."""
        result = compute_guess_colors("APPLE", "BINGO")
        expected = [
            ("A", "grey"),
            ("P", "grey"),
            ("P", "grey"),
            ("L", "grey"),
            ("E", "grey"),
        ]
        assert result == expected

    def test_some_correct_position(self):
        """Some letters in correct position."""
        result = compute_guess_colors("APPLE", "APTLY")
        assert result[0] == ("A", "green")  # A in position 0
        assert result[1] == ("P", "green")  # P in position 1

    def test_wrong_position(self):
        """Letter exists but in wrong position."""
        result = compute_guess_colors("APPLE", "LEMON")
        # E is in APPLE (position 4) but guess has it in position 1
        # L is in APPLE (position 3) but guess has it in position 0
        colors = [color for _, color in result]
        assert colors[0] == "orange"  # L in wrong position
        assert colors[1] == "orange"  # E in wrong position

    def test_duplicate_letters_both_correct(self):
        """Duplicate letters both in correct positions."""
        result = compute_guess_colors("APPLE", "APPLE")
        assert result[1] == ("P", "green")
        assert result[2] == ("P", "green")

    def test_duplicate_letters_one_correct_one_wrong(self):
        """One duplicate correct, one wrong."""
        # Target: APPLE (has P at positions 1 and 2)
        # Guess: POPUP (has P at positions 0, 2, and 4)
        result = compute_guess_colors("POPUP", "APPLE")
        # P at position 0: wrong position (target has P at 1,2) -> orange
        # O at position 1: not in target -> grey
        # P at position 2: correct position -> green
        # U at position 3: not in target -> grey
        # P at position 4: no more Ps left in target -> grey
        assert result[2][1] == "green"  # P in correct position

    def test_duplicate_in_guess_single_in_target(self):
        """Multiple instances in guess, single in target."""
        # Target: LEMON (single E)
        # Guess: EERIE (three Es)
        result = compute_guess_colors("EERIE", "LEMON")
        # E at position 0: wrong position -> orange
        # E at position 1: no more Es in target -> grey
        # R at position 2: not in target -> grey
        # I at position 3: not in target -> grey
        # E at position 4: no more Es in target -> grey
        assert result[0][1] == "orange"
        assert result[1][1] == "grey"
        assert result[4][1] == "grey"

    def test_single_in_guess_duplicate_in_target(self):
        """Single instance in guess, multiple in target."""
        # Target: APPLE (two Ps)
        # Guess: PIANO (single P)
        result = compute_guess_colors("PIANO", "APPLE")
        # P at position 0: exists in target but wrong position -> orange
        assert result[0][1] == "orange"

    def test_complex_pattern(self):
        """Complex pattern with multiple matches."""
        # Target: ROBOT
        # Guess: FLOOR
        result = compute_guess_colors("FLOOR", "ROBOT")
        # F: not in target -> grey
        # L: not in target -> grey
        # O: in target, correct position (index 2) -> green
        # O: in target at position 1, but already used for position 2 -> grey
        # R: in target but wrong position -> orange
        assert result[2][1] == "green"  # O in correct position

    def test_case_insensitive(self):
        """Coloring should work regardless of case."""
        result1 = compute_guess_colors("apple", "APPLE")
        result2 = compute_guess_colors("APPLE", "apple")
        result3 = compute_guess_colors("ApPlE", "aPpLe")

        expected = [
            ("A", "green"),
            ("P", "green"),
            ("P", "green"),
            ("L", "green"),
            ("E", "green"),
        ]

        assert result1 == expected
        assert result2 == expected
        assert result3 == expected

    def test_another_duplicate_scenario(self):
        """Test another duplicate letter scenario."""
        # Target: SPEED (two Es)
        # Guess: ERASE (two Es)
        result = compute_guess_colors("ERASE", "SPEED")
        # E at position 0: wrong position (target has E at 2,3) -> orange
        # R at position 1: not in target -> grey
        # A at position 2: not in target -> grey
        # S at position 3: wrong position (target has S at 0) -> orange
        # E at position 4: wrong position, and one E already matched -> orange
        colors = [color for _, color in result]
        assert colors[0] == "orange"  # E in wrong position
        assert colors[3] == "orange"  # S in wrong position

