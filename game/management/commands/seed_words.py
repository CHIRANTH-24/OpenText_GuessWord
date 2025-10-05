"""Management command to seed the database with initial words."""
from django.core.management.base import BaseCommand

from game.models import Word


class Command(BaseCommand):
    """Seed the database with 20 5-letter words."""

    help = "Seeds the database with 20 5-letter words for the game"

    WORDS = [
        "APPLE",
        "BRAVE",
        "CLOUD",
        "DELTA",
        "EAGER",
        "FAITH",
        "GRAPH",
        "HONEY",
        "IONIC",
        "JELLY",
        "KNIFE",
        "LEMON",
        "MAGIC",
        "NINJA",
        "OPERA",
        "PRIZE",
        "QUILT",
        "ROBIN",
        "SOLAR",
        "TANGO",
    ]

    def handle(self, *args, **options):
        """Execute the command."""
        created_count = 0
        skipped_count = 0

        for word_text in self.WORDS:
            word, created = Word.objects.get_or_create(text=word_text)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Created word: {word_text}"))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"- Skipped (already exists): {word_text}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSeeding complete! Created: {created_count}, Skipped: {skipped_count}"
            )
        )

