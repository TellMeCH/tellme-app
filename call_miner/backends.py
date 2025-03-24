import os
import logging
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from firebase_admin import auth as firebase_auth
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger('django')


class FirebaseEmailPasswordBackend(BaseBackend):
    """
    Custom authentication backend to sign in users with email and password
    via Firebase's Identity Toolkit REST API. If successful, an ID token is
    returned, which we verify using firebase_admin.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        1. Call Firebase's REST API to exchange email/password for ID token.
        2. Verify the returned ID token with Firebase Admin SDK.
        3. Get or create a Django user. Return that user on success.
        """
        if not username or not password:
            logger.error(f'Missing either email or password! (Password: {password}, Email: {username})')
            return None

        # If the emulator host is set, we'll use a local URL. Otherwise, use remote
        host = os.environ.get("FIREBASE_AUTH_EMULATOR_HOST")
        if host:
            url = f"http://{host}/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=any_key"
        else:
            api_key = settings.FIREBASE_WEB_API_KEY
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        payload = {
            "email": username,
            "password": password,
            "returnSecureToken": True
        }

        try:
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
        except requests.RequestException:
            logger.error('Failed Requesting Token!')
            return None  # returning None means "authentication failed"

        data = resp.json()
        id_token = data.get("idToken")
        if not id_token:
            logger.error('No token found in response')
            return None

        # Verify the ID token with Firebase Admin
        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
        except Exception:
            logger.error('Could not verify token')
            return None

        email = decoded_token["email"]

        # Get user in Django
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=email)
        except ObjectDoesNotExist:
            logger.error('Could not find corresponding user')
            return None

        return user

    def get_user(self, user_id):
        """
        Standard method Django calls to re-fetch a user from the database by ID.
        """
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
