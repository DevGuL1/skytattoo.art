from django.core.management.base import BaseCommand
from portfolio.services.instagram_checker import InstagramCheckerService


class Command(BaseCommand):
    help = "Sync latest Instagram posts by hashtag or username for artists and store them as native portfolio items."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force sync regardless of auto sync configuration",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting Instagram hashtag & profile sync..."))
        result = InstagramCheckerService.run_full_sync()

        if result["success"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Sync completed successfully! Fetched: {result['posts_fetched']}, Created: {result['items_created']}"
                )
            )
            self.stdout.write(result["details"])
        else:
            self.stdout.write(self.style.ERROR(f"Sync failed: {result.get('details')}"))
