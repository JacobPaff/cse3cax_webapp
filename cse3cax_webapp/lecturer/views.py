# 
# Views for Lecturer Roster and Subject Instance Management
# ==========================================================
# This file defines the view functions for handling the lecturer's roster, 
# fetching lecturer instances, and displaying detailed subject instance information.
# The views utilize caching to optimize performance and ensure that data is displayed efficiently.
#
# File: views.py
# Author: Jacob Paff
# Revisions:
#   - 19-09-24: Initial file created by Jacob Paff. Added caching for lecturer instance data and basic views for lecturer roster and subject instance info.
#   - 23-09-24: Added caching to the lecturer instance list for performance improvement.
#   - 05-10-24: Added user-based filtering for the subject instance list to ensure correct data display based on authentication.
#

from django.shortcuts import get_object_or_404, render
from datetime import timedelta
from core.models import SubjectInstanceLecturer, SubjectInstance
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache

# Helper function to check if the user is a lecturer
def is_lecturer(user):
    return user.is_authenticated and (user.role.role_id == 'Lecturer' or user.role.role_id == 'Testing')

# Helper function to retrieve and cache lecturer instance information
def lecturer_instances_info(user):
    # Generate a unique cache key for this user
    cache_key = f'lect_inst_info_{user.user_id}'
    
    # Check if the data is already cached for this user
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # Initialize years and months
    years = set()
    months = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    # Get all subject instances where the user is a lecturer
    subject_instances_objects = SubjectInstanceLecturer.objects.filter(
        user_id=user.pk).select_related('subject_instance', 'subject_instance__subject')
    
    subject_instances_list = []

    # Loop through each subject instance and prepare the data
    for subject_instances_object in subject_instances_objects:
        subject_instance = subject_instances_object.subject_instance
        subject = subject_instance.subject
        start_date = subject_instance.start_date
        end_month = (start_date + timedelta(weeks=12) + timedelta(days=-2)).month
        years.add(start_date.year)

        # Add the subject instance to the list
        subject_instances_list.append({
            'subject_id': subject.subject_id,
            'subject_name': subject.subject_name,
            'start_year': start_date.year,
            'start_month': start_date.month,
            'instance_id': subject_instance.instance_id,
            'end_month': end_month,  # 3-month range for the subject
        })

    years = sorted(list(years))

    # Cache the result for this user for 10 minutes
    cache.set(cache_key, (years, months, subject_instances_list), 600)

    return years, months, subject_instances_list

# View to display the lecturer instance list in a table format
@user_passes_test(is_lecturer, login_url='login_redirect')
def lecturer_instance_list(request):
    current_user = request.user
    years, months, subject_instances_list = lecturer_instances_info(current_user)
    context = {
        'years': years,
        'months': months,
        'subject_instances_list': subject_instances_list,
    }
    return render(request, 'lecturer_instance_list.html', context)

# View to display the lecturer's roster
@user_passes_test(is_lecturer, login_url='login_redirect')
def lecturer_roster(request):
    current_user = request.user
    years, months, subject_instances_list = lecturer_instances_info(current_user)
    context = {
        'years': years,
        'months': months,
    }
    return render(request, 'lecturer_roster.html', context)

# View to display detailed information about a specific subject instance
def subject_instance_info(request):
    instance_id = request.GET.get('instance_id')
    subject_instance = get_object_or_404(SubjectInstance, instance_id=instance_id)
    context = {
        'subject_instance': subject_instance,
        'end_date': subject_instance.start_date + timedelta(weeks=12) + timedelta(days=-2),
        'lecturers': subject_instance.lecturer.all(),
        'subject_name': subject_instance.subject.subject_name
    }
    return render(request, 'subject_instance_info.html', context)
