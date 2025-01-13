import logging
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model
from django.conf import settings
from firebase_admin import auth as firebase_auth, exceptions as firebase_exceptions

logger = logging.getLogger(__name__)


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Authentication class for Django Rest Framework to authenticate requests using JWT Bearer Tokens supplied by a
    Firebase application.
    """
    HEADER_SCHEMA = 'Bearer '

    def authenticate(self, request):
        """
        Authenticate using Firebase JWT.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_header:
            logger.debug("No Authorization header found")
            return None

        if auth_header.startswith(self.HEADER_SCHEMA):
            id_token = auth_header[len(self.HEADER_SCHEMA):]
            logger.debug("Got ID Token")
            try:
                decoded_token = firebase_auth.verify_id_token(id_token, check_revoked=True)
                logger.debug("Successfully decoded token")

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

        logger.debug("Invalid Authorization header schema")
        return None
