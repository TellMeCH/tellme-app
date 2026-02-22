from django.core.management.base import BaseCommand
from django.utils import timezone
from tellme.call_miner.models import EphemeralProcessingToken


class Command(BaseCommand):
    help = "Delete all EphemeralProcessingToken instances whose expires_at is in the past."

    def handle(self, *args, **options):
        deleted_count, _ = EphemeralProcessingToken.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()
        self.stdout.write(
            self.style.SUCCESS(f"Purged {deleted_count} expired ephemeral token(s).")
        )
