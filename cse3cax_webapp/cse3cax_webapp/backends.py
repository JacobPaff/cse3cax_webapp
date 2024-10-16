# 
# Cognito Authentication Backend
# ===============================
# This file defines a custom authentication backend for handling Cognito user authentication.
# It interacts with the Django UserModel to authenticate users based on Cognito-provided user information.
#
# File: backends.py
# Author: Jacob Paff
# Revisions:
#   - 19-09-24: Initial file created by Jacob Paff. Added basic authentication via Cognito user_info.
#

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from core.models import UserProfile

UserModel = get_user_model()

class CognitoBackend(BaseBackend):
    """
    Custom authentication backend to authenticate users using Cognito-provided user info.
    """

    def authenticate(self, request, user_info=None):
        """
        Authenticate user based on information from Cognito.

        Args:
            request: The HTTP request object.
            user_info (dict): User information provided by Cognito (contains email, etc.).

        Returns:
            UserProfile or None: The authenticated user or None if authentication fails.
        """
        if user_info is None:
            return None

        # Extract necessary information from user_info
        email = user_info.get('email')

        if not email:
            return None

        # Try to get the user from the database
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None

        # Return the authenticated user
        return user

    def get_user(self, user_id):
        """
        Retrieve the user instance by their primary key.

        Args:
            user_id (int): The primary key of the user.

        Returns:
            UserProfile or None: The retrieved user or None if not found.
        """
        try:
            user = UserModel.objects.get(pk=user_id)
            return user
        except UserModel.DoesNotExist:
            return None
