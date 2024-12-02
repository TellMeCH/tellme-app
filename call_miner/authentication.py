import logging
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model
from django.conf import settings
from firebase_admin import auth as firebase_auth, exceptions as firebase_exceptions

logger = logging.getLogger(__name__)


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Authentication class for Django Rest Framework to authenticate requests
    using either JWT Bearer Tokens supplied by a Firebase application
    or API tokens for a specific superuser account.
    """
    HEADER_SCHEMA = 'Bearer '
    API_TOKEN_SCHEMA = 'Token '

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_header:
            logger.debug("No Authorization header found")
            return None

        if auth_header.startswith(self.HEADER_SCHEMA):
            return self.authenticate_firebase(auth_header[len(self.HEADER_SCHEMA):])

        if auth_header.startswith(self.API_TOKEN_SCHEMA):
            return self.authenticate_api_token(auth_header[len(self.API_TOKEN_SCHEMA):])

        logger.debug("Invalid Authorization header schema")
        return None

    @staticmethod
    def authenticate_firebase(id_token):
        """
        Authenticate using Firebase JWT.
        """
        logger.debug(f"Got ID Token: {id_token}")
        try:
            decoded_token = firebase_auth.verify_id_token(id_token, check_revoked=True)
            logger.debug(f"Successfully decoded token: {decoded_token}")

            # Handle unverified Emails
            if not decoded_token.get('email_verified', False):
                logger.warning('Tokens with unverified emails are not allowed')
                return None
        except firebase_exceptions.FirebaseError as e:
            raise exceptions.AuthenticationFailed(f'Invalid Firebase token - {e}')
        except firebase_auth.RevokedIdTokenError:
            logger.warning("JWT token has been revoked", exc_info=True)
            return None
        except Exception as e:
            logger.warning("Unknown exception while verifying token", exc_info=True)
            raise exceptions.AuthenticationFailed(f'Invalid Firebase token - {e}')

        user = get_user_model().objects.get(id=decoded_token['uid'])

        if user.email == settings.PROCESSING_PIPELINE_USER:
            raise exceptions.AuthenticationFailed(f'Processing Pipeline should only authenticate with API Token')
        return user, None

    @staticmethod
    def authenticate_api_token(token):
        """
        Authenticate using API token.
        """
        try:
            # Validate the token matches the superuser
            if token == settings.PROCESSING_PIPELINE_KEY:
                user = get_user_model().objects.get(email=settings.PROCESSING_PIPELINE_USER)
                return user, None
            else:
                raise ValueError('API Token does not match expected value!')
        except Exception as e:
            logger.warning("Error authenticating API token", exc_info=True)
            raise exceptions.AuthenticationFailed(f'Invalid API token - {e}')
