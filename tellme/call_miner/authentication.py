import base64
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

    Used for authenticating call to ViewSets
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

            if settings.TELLME_ENV == 'dev':
                try:
                    decoded_token = firebase_auth.verify_id_token(id_token, check_revoked=True)
                    uid = decoded_token['uid']
                    user_email = decoded_token['email']
                    email_verified = decoded_token.get('email_verified', False)
                    logger.debug("Successfully decoded token")

                except firebase_exceptions.FirebaseError as e:
                    logger.warning("Invalid Firebase token", exc_info=True)
                    raise exceptions.AuthenticationFailed(f'Invalid Firebase token - {e}')
                except firebase_auth.RevokedIdTokenError as e:
                    logger.warning("JWT token has been revoked", exc_info=True)
                    raise exceptions.AuthenticationFailed(f'Revoked Firebase token - {e}')
                except Exception as e:
                    logger.warning("Unknown exception while verifying token", exc_info=True)
                    raise exceptions.AuthenticationFailed(f'Invalid Firebase token - {e}')

            else:  # Staging and Prod
                user_info_encoded = request.headers.get('x-apigateway-api-userinfo')
                if not user_info_encoded:
                    logger.warning("User info header missing", exc_info=True)
                    raise exceptions.AuthenticationFailed("User info header missing")

                try:
                    decoded_bytes = base64.urlsafe_b64decode(userinfo_encoded + "==")
                    user_info = json.loads(decoded_bytes.decode("utf-8"))
                    uid = user_info.get("user_id")
                    user_email = user_info.get("email")
                    email_verified = user_info.get("email_verified", False)
                    logger.debug("Successfully decoded header")
                    if not uid:
                        logger.warning("No UID found in token", exc_info=True)
                        raise exceptions.AuthenticationFailed("No UID found in token")
                except Exception as e:
                    logger.warning("Unknown exception while decoding user info header", exc_info=True)
                    raise exceptions.AuthenticationFailed(f'Invalid User Info Header - {e}')

            User = get_user_model()
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                firebase_auth.delete_user(uid)
                logger.warning(f"No user account exists for {user_email}.")
                raise exceptions.AuthenticationFailed(f"No user account exists for {user_email}.")

            # Handle unverified Emails
            if not email_verified:
                user.send_verification_email()
                logger.info(f"Email verification required for {user_email}.")
                raise exceptions.AuthenticationFailed(
                    f"Please verify your email and try again. Instructions have been sent to {user_email}."
                )

            if user.email == settings.PROCESSING_PIPELINE_USER:
                raise exceptions.AuthenticationFailed(f'Processing Pipeline should only authenticate with API Token')
            return user, None

        logger.debug("Invalid Authorization header schema")
        return None
