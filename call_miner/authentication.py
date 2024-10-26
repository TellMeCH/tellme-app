import logging
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model
from firebase_admin import auth as firebase_auth, exceptions as firebase_exceptions

logger = logging.getLogger(__name__)


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Authentication class for Django Rest Framework to authenticate requests
    using JWT Bearer Tokens supplied by a Firebase application.
    """
    HEADER_SCHEMA = 'Bearer '

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_header:
            logger.debug("No Authorization header found")
            return None

        # Validate Authorization header schema
        if not auth_header.startswith(self.HEADER_SCHEMA):
            logger.debug(f"Authorization header does not start with '{self.HEADER_SCHEMA}'")
            return None

        # Get base64 encoded token from header
        _, id_token = auth_header.split(self.HEADER_SCHEMA)
        logger.debug(f"Got ID Token: {id_token}")

        try:
            # Attempt to decode and verify token
            decoded_token = firebase_auth.verify_id_token(id_token, check_revoked=True)
            logger.debug(f"Successfully decoded token: {decoded_token}")

            # Handle unverified Emails
            if not decoded_token['email_verified']:
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
        return user, None
