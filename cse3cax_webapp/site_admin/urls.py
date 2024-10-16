
# 
# URL Configuration for User Management
# ======================================
# This file defines the URL patterns for managing users within the application. 
# It includes paths for adding, editing, deleting users, setting expertise, and displaying user lists.
#
# File: urls.py
# Author: Jacob Paff
#

from django.urls import path
from . import views

urlpatterns = [
    path('user_management/', views.user_management, name='user_management'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('set_expertise/<int:user_id>/', views.set_expertise, name='set_expertise'),
    path('add_user/', views.add_user, name='add_user'),
    path('user_list/', views.user_list, name='user_list'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('message_modal/', views.message_modal, name='message_modal'),
    path('confirm_delete_user/<int:user_id>/', views.confirm_delete_user, name='confirm_delete_user'),
]
