# 
# Django App Configuration
# =========================
# This file defines the configuration for the "core" application within the project.
#
# File: apps.py
# Author: Jacob Paff
# Revisions:
#   - 17-09-24: Initial file created by Jacob Paff. Configured the "core" app with default primary key field.
# 

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Core application configuration class for the project.
    Sets the default auto field for models and assigns the name of the app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
