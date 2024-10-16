# 
# URL Configuration for University Testing System
# ===============================================
# This file defines the URL patterns for the core application, including the home page, 
# login redirection, Cognito callback, logout, and health check endpoints.
#
# File: urls.py
# Author: Jacob Paff
# Revisions:
#   - 17-09-24: Initial file created by Jacob Paff. Added routes for home, login redirect, and Cognito callback.
#   - 19-09-24: Added set_testing_role and health_check routes for testing and system monitoring.
#

from django.urls import path
from django.shortcuts import redirect
from . import views

# URL Patterns for the application
urlpatterns = [
    path('', views.role_redirect, name='home'),  # Redirect users based on role
    path('login/', views.login_redirect, name='login_redirect'),  # Redirect to login page
    path('cognito_callback/', views.cognito_callback, name='cognito_callback'),  # Handle Cognito authentication callback
    path('logout/', views.logout_view, name='logout'),  # Logout functionality
    path('set_testing_role/', views.set_testing_role, name='set_testing_role'),  # Assign testing role to specific users
    path('health/', views.health_check, name='health_check'),  # System health check endpoint
]
