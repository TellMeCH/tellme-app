from django.core.management.base import BaseCommand, CommandError
from firebase_admin import auth
from django.conf import settings
from call_miner.models import User


class Command(BaseCommand):
    help = "Creates superusers for remote API execution"

    def handle(self, *args, **options):

        try:
            self.stdout.write('Creating Superuser Account for Processing Pipeline')
            user = User.objects.create_superuser(
                username='processing_pipeline',
                password=settings.PROCESSING_PWD,
                email=f'processing.{settings.TELLME_ENV}@tell-me.ch'
            )
            auth.update_user(
                user.id,
                email_verified=True
            )
        except Exception as e:
            raise CommandError(f'Failed to create Superuser Account for Processing Pipeline: {e}')

        try:
            self.stdout.write('Creating Superuser Account for Application Management')
            user = User.objects.create_superuser(
                username='app_admin',
                password=settings.APP_ADMIN_PWD,
                email=f'app.admin.{settings.TELLME_ENV}@tell-me.ch'
            )
            auth.update_user(
                user.id,
                email_verified=True
            )
        except Exception as e:
            raise CommandError(f'Failed to create Superuser Account for Processing Pipeline: {e}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created superuser accounts.')
        )
