# URL Configuration for Lecturer Roster Management
# ================================================
# This file defines the URL patterns for managing the lecturer roster and subject instances.
# It includes paths for viewing the lecturer roster, fetching lecturer instance lists, 
# and retrieving detailed subject instance information.
#
# File: urls.py
# Author: Jacob Paff

from django.urls import path
from . import views

urlpatterns = [
    path('lecturer_roster', views.lecturer_roster, name='lecturer_roster'),
    path('lecturer_instance_list', views.lecturer_instance_list, name='lecturer_instance_list'),
    path('subject_instance_info/', views.subject_instance_info, name='subject_instance_info'),
]
