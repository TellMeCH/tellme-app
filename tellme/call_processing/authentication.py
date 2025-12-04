import logging
import hashlib
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from tellme.call_miner.models import OrganizationAPIKey

logger = logging.getLogger(__name__)


class OrganizationAPIKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class that checks for a valid API key in the Authorization header.
    Expected header format (by convention): 'Authorization: Api-Key <API_KEY>'
    """
    KEYWORD = 'X-API-KEY'

    def authenticate(self, request):

        # Check for API key in X-Forwarded-Authorization
        auth_header = request.headers.get('X-Forwarded-Authorization')
        if not auth_header:
            auth_header = request.headers.get('Authorization')  # TODO: Remove once API Gateway Access is enforced
            if not auth_header:
                logger.debug("No Authorization or X-Forwarded-Authorization header found")
                return None

        # Check if the header starts with the expected keyword (f.e X-API-KEY <key>)
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.KEYWORD:
            logger.debug("Invalid Authorization header schema")
            return None

        api_key = parts[1]
        logger.debug(f"Got API Key")

        # Check whether there is a matching key in the DB
        hashed_key = hashlib.sha256((settings.HASH_KEY + api_key + settings.HASH_KEY).encode('utf-8')).hexdigest()
        try:
            org_api_key = OrganizationAPIKey.objects.get(hashed_api_key=hashed_key)
            logger.debug('Successfully matched API Key with Organization')
        except OrganizationAPIKey.DoesNotExist:
            logger.debug('Could not match API Key with Organization')
            raise exceptions.AuthenticationFailed("Invalid API key.")

        # If a key is found, check the expiry date
        if org_api_key.expires < timezone.now():
            logger.debug(f'Provided API key expired on {org_api_key.expires}')
            raise exceptions.AuthenticationFailed("API key expired.")
        return org_api_key.organization, None


class ProcessingKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class that checks for a valid token representing the Cloud Task Manager, used to call the
    processing pipeline.
    """
    API_TOKEN_SCHEMA = 'Token '

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_header:
            logger.debug("No Authorization header found")
            return None

        if auth_header.startswith(self.API_TOKEN_SCHEMA):
            token = auth_header[len(self.API_TOKEN_SCHEMA):]
            try:
                # Validate the token matches the superuser
                if token == settings.PROCESSING_PIPELINE_KEY:
                    logger.debug('Successfully matched token with key in settings')
                    user = get_user_model().objects.get(email=settings.PROCESSING_PIPELINE_USER)
                    logger.debug('Successfully retrieved processing pipeline account')
                    return user, None
                else:
                    logger.debug('API Token does not match expected value!')
                    raise ValueError('API Token does not match expected value!')
            except Exception as e:
                raise exceptions.AuthenticationFailed(
                    f'Invalid API token. Probably processing pipeline account has not been created. - {e}'
                )
        return None

