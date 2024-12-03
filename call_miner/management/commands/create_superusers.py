import io
import environ
from google.cloud import secretmanager
from django.core.management.base import BaseCommand, CommandError
from firebase_admin import auth
from django.conf import settings
from call_miner.models import User

env = environ.Env()

"""
This management command is originally meant to be run remotely. In the meantime however, it has to be called
locally with the following adjustments:
- ./cloud_setup/cloud-sql-proxy --port=5433 --gcloud-auth $GOOGLE_CLOUD_PROJECT:$REGION:$INSTANCE_NAME
- export APP_ADMIN_PWD=...
- export PROCESSING_PWD=...
- export USE_CLOUD_SQL_AUTH_PROXY=true
- Make sure FIREBASE_AUTH_EMULATOR_HOST is not included in local .env
- Run python manage.py runserver 0.0.0.0:8080
"""


class Command(BaseCommand):
    help = "Creates superusers for remote API execution"

    def handle(self, *args, **options):

        try:
            if not (env('APP_ADMIN_PWD', default=None) and env('PROCESSING_PWD', default=None)):
                self.stdout.write('Could not find superuser passwords in environment variables. Loading from Secret '
                                  'Manager...')

                client = secretmanager.SecretManagerServiceClient()
                secret_name = env("PASSWORDS_NAME")
                secret_path = f"projects/{settings.GOOGLE_CLOUD_PROJECT}/secrets/{secret_name}/versions/latest"
                response = client.access_secret_version(name=secret_path)
                payload = response.payload.data.decode("UTF-8")
                if '#' in payload:
                    raise Exception('Watch out with special characters in your passwords! This step will mess with them')
                env.read_env(io.StringIO(payload))

            app_admin_pwd = env('APP_ADMIN_PWD')
            processing_pwd = env('PROCESSING_PWD')
        except Exception as e:
            raise CommandError(f'Failed to load superuser account passwords: {e}')

        # Helper function to delete a user both locally and from Firebase
        def delete_user(username):
            try:
                existing_user = User.objects.filter(username=username).first()
                if existing_user:
                    self.stdout.write(f'Deleting existing user: {username}')
                    # Delete user from Firebase if exists
                    try:
                        auth.delete_user(existing_user.id)
                        self.stdout.write(f'Deleted Firebase user: {existing_user.id}')
                    except auth.UserNotFoundError:
                        self.stdout.write(f'No Firebase user found for: {existing_user.id}')
                    # Delete the user from Django
                    existing_user.delete()
                    self.stdout.write(f'Deleted Django user: {username}')
            except Exception as e:
                raise CommandError(f'Failed to delete user {username}: {e}')

        # Delete existing accounts if found
        delete_user('app_admin')
        delete_user('processing_pipeline')

        try:
            self.stdout.write('Creating Superuser Account for Application Management')
            user = User.objects.create_superuser(
                username='app_admin',
                password=app_admin_pwd,
                email=f'app.admin.{settings.TELLME_ENV}@tell-me.ch'
            )
            auth.update_user(
                user.id,
                email_verified=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superuser account for application management: {user.id}.')
            )
        except Exception as e:
            raise CommandError(f'Failed to create Superuser Account for Application Management: {e}')

        try:
            self.stdout.write('Creating Superuser Account for Processing Pipeline')
            user = User.objects.create_superuser(
                username='processing_pipeline',
                password=processing_pwd,
                email=settings.PROCESSING_PIPELINE_USER
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superuser account for processing pipeline: {user.id}.')
            )
        except Exception as e:
            raise CommandError(f'Failed to create Superuser Account for Processing Pipeline: {e}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created superuser accounts.')
        )
