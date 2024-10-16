# 
# Django Admin Configuration
# ==========================
# This file configures the Django admin interface for managing UserProfile, Role, and Subject models.
# By registering these models, they become manageable through the Django admin panel.
#
# File: admin.py
# Author: Jacob Paff
# Revisions:
#   - 17-09-24: Initial file created by Jacob Paff. Registered UserProfile, Role, and Subject models.
# 

from django.contrib import admin

from .models import UserProfile, Role, Subject

# Register models for the admin interface
admin.site.register(UserProfile)
admin.site.register(Role)
admin.site.register(Subject)
