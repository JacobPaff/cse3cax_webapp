from django.core.management.base import BaseCommand
from core.models import UserProfile, Role
import json


class Command(BaseCommand):  # Make sure this class is named "Command"
    help = 'Load user data from JSON file into UserProfile'

    def handle(self, *args, **kwargs):
        # Load your JSON data
        with open('user_data.json') as f:
            user_data = json.load(f)

        for record in user_data:
            if record['model'] == 'core.userprofile':
                fields = record['fields']

                # Create the user profile, using create_user from UserProfileManager
                user = UserProfile.objects.create_user(
                    role=Role.objects.get(role_id=fields['role']),
                    email=fields['email'],
                    first_name=fields.get('first_name'),
                    last_name=fields.get('last_name'),
                    fte_percentage=fields.get('fte_percentage'),
                    honorific=fields.get('honorific'),
                )
                print(f"Created user {user.email}")
