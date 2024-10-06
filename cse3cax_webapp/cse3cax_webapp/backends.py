# your_app_name/backends.py

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from core.models import UserProfile

UserModel = get_user_model()


class CognitoBackend(BaseBackend):
    def authenticate(self, request, user_info=None):
        # Assuming user_info is a dictionary with user details from Cognito
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
            # # Optionally, create a new user if not found
            # user = UserModel.objects.create_user(
            #     email=email,
            #     # Include other fields as necessary
            # )
            # user.set_unusable_password()
            # user.save()
            return None
        # Return the authenticated user
        return user

    def get_user(self, user_id):
        try:
            user = UserModel.objects.get(pk=user_id)
            return user
        except UserModel.DoesNotExist:
            return None
