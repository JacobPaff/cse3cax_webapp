#
# Views for Managing Subject Instances and Lecturer Assignments
# =============================================================
# This file defines the views for handling subject instances, including creating, editing, and deleting instances.
# It also includes views for managing lecturer assignments, recalculating workloads, and viewing instance details.
# The views use caching where appropriate and implement role-based access control for Manager and Testing roles.
#
# File: views.py
# Author: Jacob Paff

from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from core.models import LecturerWorkload, SubjectInstance, Subject, SubjectInstanceLecturer, UserProfile, WorkloadManager, LecturerExpertise
from .forms import SubjectInstanceForm
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from datetime import timedelta
import datetime

# Utility function to check if the user is a Manager or Testing role


def is_manager(user):
    return user.is_authenticated and (user.role.role_id == 'Manager' or user.role.role_id == 'Testing')

# View to display all subject instances


@user_passes_test(is_manager, login_url='login_redirect')
def subject_instances(request):
    subjects = Subject.objects.all()
    return render(request, 'subject_instances.html', {'subjects': subjects})

# View to display the list of subject instances, with optional search functionality

def filter_subject_instances_by_month(subject_instances, selected_month=''):
    # Apply the month filter if provided
    year, month = map(int, selected_month.split('-'))
    start_date = datetime.date(year, month, 1)
    end_date = start_date + timedelta(weeks=12) - timedelta(days=2)

    subject_instances = subject_instances.filter(
        start_date__gte=start_date,
        start_date__lte=end_date
    )
    return subject_instances

def filter_subject_instances_by_search(subject_instances, query=''):
    """
    Helper function to filter subject instances by search query
    """
    subject_instances = subject_instances.filter(
        Q(subject__subject_name__icontains=query) |
        Q(subject__subject_id__icontains=query) |
        Q(subjectinstancelecturer__user__first_name__icontains=query) |
        Q(subjectinstancelecturer__user__last_name__icontains=query)
    ).distinct()
    return subject_instances



@user_passes_test(is_manager, login_url='login_redirect')
def instance_list(request):
    query = request.GET.get('search', '')
    selected_month = request.GET.get('month', '')  # Get the selected month (YYYY-MM format)
    subject_instances = SubjectInstance.objects.all()

    # Apply the search query filter if provided
    if query:
        subject_instances = filter_subject_instances_by_search(subject_instances, query)

    # Filter by the selected month and the next two months
    if selected_month:
        subject_instances = filter_subject_instances_by_month(subject_instances, selected_month)

    return render(request, 'instance_list.html', {'subject_instances': subject_instances})


# View to add a new subject instance


@user_passes_test(is_manager, login_url='login_redirect')
def add_subject_instance(request):
    if request.method == "POST":
        form = SubjectInstanceForm(request.POST)
        if form.is_valid():
            form.save()
            # no content
            return HttpResponse(status=204, headers={'Hx-Trigger': 'instanceListChanged'})
    else:
        form = SubjectInstanceForm()
    form_string = 'Create Subject Instance'
    return render(request, 'modals/form_modal.html', {'form': form, 'form_string': form_string})

# View to edit an existing subject instance


@user_passes_test(is_manager, login_url='login_redirect')
def edit_subject_instance(request, instance_id):
    """
    View to edit an existing subject instance. This view handles the request to edit a subject instance.
    If the request is a POST, it will validate the form data and save the subject instance. If the enrollments
    have changed, it will call the update_lecturer_workload method to update the workloads for associated lecturers.
    If the request is not a POST, it will render a form with the current subject instance data.

    Args:
        request (HttpRequest): The request object
        instance_id (int): The id of the subject instance to edit

    Returns:
        HttpResponse: A response with the updated html or a 204 status code with headers to trigger the
            hx-socket to update the subject instance list and/or the overloaded lecturers list.
    """
    subject_instance = get_object_or_404(
        SubjectInstance, instance_id=instance_id)
    if request.method == "POST":
        form = SubjectInstanceForm(request.POST, instance=subject_instance)
        if form.is_valid():
            # ensure html is updated
            triggers = 'instanceListChanged'
            # Get the student threshold
            student_threshold = WorkloadManager.STUDENT_THRESHOLD
            # Get the current enrollment count before saving the form
            current_enrollments = subject_instance.enrollments or 0  # Default to 0 if None
            # Save the form to update the SubjectInstance
            form.save()
            # Get the updated enrollment count from the form data
            new_enrollments = form.cleaned_data.get('enrollments', 0)
            # Check if enrollments have changed and call update workload
            if current_enrollments > student_threshold or new_enrollments > student_threshold:
                if subject_instance.update_lecturer_workload():
                    triggers += ', overloadedLecturers'
            return HttpResponse(status=204, headers={'Hx-Trigger': triggers})
    else:
        form = SubjectInstanceForm(instance=subject_instance)
    form_string = 'Edit Subject Instance'
    return render(request, 'modals/form_modal.html', {'form': form, 'form_string': form_string})


# View to confirm the deletion of a subject instance
@user_passes_test(is_manager, login_url='login_redirect')
def confirm_delete_instance(request, instance_id):
    instance = get_object_or_404(SubjectInstance, instance_id=instance_id)
    form_string = f'Are you sure you want to delete instance {instance.subject}-{instance.month}/{instance.year}?'
    delete_url = reverse("delete_instance", kwargs={
                         "instance_id": instance.instance_id})
    hx_post_attribute = f'hx-post="{delete_url}"'
    context = {
        'form_string': form_string,
        'hx_post_attribute': hx_post_attribute,
    }
    return render(request, 'modals/confirm_delete_modal.html', context)

# View to delete a subject instance and update workloads as necessary


@user_passes_test(is_manager, login_url='login_redirect')
def delete_instance(request, instance_id):
    subject_instance = get_object_or_404(
        SubjectInstance, instance_id=instance_id)
    # ensure workload is recalculated on delete
    subject_instance.delete_and_update_workload()
    # No content response
    return HttpResponse(status=204, headers={'Hx-Trigger': 'instanceListChanged'})

# View to render the modal for assigning lecturers to a subject instance


@user_passes_test(is_manager, login_url='login_redirect')
def assign_lecturer_instance(request):
    instance_id = request.GET.get('instance_id')
    return render(request, 'assign_lecturer_instance.html', {'instance_id': instance_id})

# View to list lecturers assigned to a specific subject instance


@user_passes_test(is_manager, login_url='login_redirect')
def lecturer_list(request):
    query = request.GET.get('search', '')
    instance_id = request.GET.get('instance_id')

    # Get the subject instance
    subject_instance = SubjectInstance.objects.get(pk=instance_id)
    start_month = subject_instance.start_date.month
    year = subject_instance.start_date.year

    # Get lecturers assigned to the subject instance
    assigned_lecturers = UserProfile.objects.filter(
        subjectinstancelecturer__subject_instance=instance_id
    )

    # Get lecturers who have expertise in the subject of this instance
    expertised_lecturers = UserProfile.objects.filter(
        lecturerexpertise__subject=subject_instance.subject
    )

    # Combine both filters: lecturers with expertise and assigned to the subject instance
    lecturer_list = expertised_lecturers

    # Apply the search query to filter by first or last name
    if query:
        lecturer_list = lecturer_list.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

    # Create a list to store lecturers with their metadata for sorting
    lecturer_data = []

    # For each lecturer, find the maximum workload for the 3 months the instance is active
    for lecturer in lecturer_list:
        workload_percentages = [
            lecturer.workload_percentage_for_month(start_month, year),
            lecturer.workload_percentage_for_month(start_month + 1, year),
            lecturer.workload_percentage_for_month(start_month + 2, year)
        ]

        # Add max workload percentage to the lecturer object
        lecturer.max_workload_percent = max(workload_percentages)

        # Check if the lecturer is assigned to the instance
        is_assigned = assigned_lecturers.filter(pk=lecturer.pk).exists()

        # Count how many subjects this lecturer has expertise in
        expertise_count = LecturerExpertise.objects.filter(
            user=lecturer).count()

        # Store the lecturer and sorting info
        lecturer_data.append({
            'lecturer': lecturer,
            'is_assigned': is_assigned,
            'max_workload_percent': lecturer.max_workload_percent,
            'expertise_count': expertise_count,
        })

    # Sort the lecturers first by assigned (True first), then by max_workload_percent, then by expertise_count
    sorted_lecturers = sorted(
        lecturer_data,
        key=lambda x: (not x['is_assigned'], -
                       x['max_workload_percent'], -x['expertise_count'])
    )

    # Pass only the sorted lecturers back to the template
    return render(request, 'lecturer_list.html', {
        'lecturer_list': [item['lecturer'] for item in sorted_lecturers],
        'assigned_lecturers': assigned_lecturers,
        'instance_id': instance_id,
    })

# View to add a lecturer to a subject instance


@user_passes_test(is_manager, login_url='login_redirect')
def add_lecturer_instance(request):
    instance_id = request.GET.get('instance_id')
    subject_instance = get_object_or_404(
        SubjectInstance, instance_id=instance_id)
    lecturer_id = request.GET.get('lecturer_id')
    lecturer = get_object_or_404(UserProfile, user_id=lecturer_id)
    # ensure html is updated
    triggers = 'instanceListChanged'
    # Add the lecturer to the subject instance lecturer and upates workload
    if subject_instance.add_lecturer(lecturer):
        triggers += ', overloadedLecturers'
    return HttpResponse(status=202, headers={'Hx-Trigger': triggers})

# View to remove a lecturer from a subject instance


@user_passes_test(is_manager, login_url='login_redirect')
def remove_lecturer_instance(request):
    instance_id = request.GET.get('instance_id')
    subject_instance = get_object_or_404(
        SubjectInstance, instance_id=instance_id)
    lecturer_id = request.GET.get('lecturer_id')
    lecturer = get_object_or_404(UserProfile, user_id=lecturer_id)
    # ensure html is updated
    triggers = 'instanceListChanged'
    # Remove the lecturer from the subject instance lecturer
    if subject_instance.remove_lecturer(lecturer):
        triggers += ', overloadedLecturers'
    return HttpResponse(status=202, headers={'Hx-Trigger': triggers})


# View to assign a roster to subject instances


@user_passes_test(is_manager, login_url='login_redirect')
def assign_roster(request):
    return render(request, 'assign_roster.html')


@user_passes_test(is_manager, login_url='login_redirect')
def instance_calendar(request):
    print('calendar', request.GET.get) 
    query = request.GET.get('search', '')
    selected_month = request.GET.get('month', '')  # Get the selected month (YYYY-MM format)
    subject_instances = SubjectInstance.objects.all()
    # Filter by query if provided
    if query:
        subject_instances = filter_subject_instances_by_search(subject_instances, query)

    # Filter by the selected month and the next two months
    if selected_month:
        subject_instances = filter_subject_instances_by_month(subject_instances, selected_month)
    
    years, months, _ = all_instances_info()

    # Check if any lecturer in the filtered instances is overloaded
    for subject_instance in subject_instances:
        subject_instance.is_lecturer_overloaded = LecturerWorkload.objects.filter(
            user_profile__in=subject_instance.lecturer.all(),
            month=subject_instance.start_date.month,
            year=subject_instance.start_date.year,
            is_overloaded=True
        ).exists()
    
    context = {
        'years': years,
        'months': months,
        'subject_instances_list': subject_instances,
    }
    
    return render(request, 'instance_calendar.html', context)















# # View to render the subject instance calendar

# @user_passes_test(is_manager, login_url='login_redirect')
# def instance_calendar(request):
#     years, months, subject_instances_list = all_instances_info()

#     for subject_instance in subject_instances_list:
#         # Check if any lecturer in this subject instance is overloaded
#         subject_instance.is_lecturer_overloaded = LecturerWorkload.objects.filter(
#             user_profile__in=subject_instance.lecturer.all(),
#             month=subject_instance.start_date.month,
#             year=subject_instance.start_date.year,
#             is_overloaded=True
#         ).exists()
    
#     context = {
#         'years': years,
#         'months': months,
#         # A dictionary with subjects and their active months
#         'subject_instances_list': subject_instances_list,
#     }
#     # lecturers' : subject_instance.lecturer.all(),
#     return render(request, 'instance_calendar.html', context)



def all_instances_info():
    # Check if the data is already cached for this user
    # cached_data = cache.get('instance_data')
    # if cached_data:
    #     return cached_data

    years = set()

    months = {
        1: 'Jan',
        2: 'Feb',
        3: 'Mar',
        4: 'Apr',
        5: 'May',
        6: 'Jun',
        7: 'Jul',
        8: 'Aug',
        9: 'Sep',
        10: 'Oct',
        11: 'Nov',
        12: 'Dec'
    }

    # Fetch all SubjectInstance objects
    subject_instances = SubjectInstance.objects.select_related('subject').prefetch_related('lecturer').all()

    # Add years and calculate end_month for each instance
    for subject_instance in subject_instances:
        start_date = subject_instance.start_date
        end_date = start_date + timedelta(weeks=12) - timedelta(days=2)  # Calculate end date (3 months)
        subject_instance.end_month = end_date.month  # Add end_month attribute to each instance

        years.add(start_date.year)
        if end_date.year > start_date.year:
            years.add(end_date.year)

    years = sorted(list(years))

    # Cache the result for this user for 10 minutes
    # cache.set('instance_data', (years, months, subject_instances), 600)

    return years, months, subject_instances

# def all_instances_info():
#     # Check if the data is already cached for this user
#     cached_data = cache.get('instance_data')
#     if cached_data:
#         return cached_data

#     years = set()

#     months = {
#         1: 'Jan',
#         2: 'Feb',
#         3: 'Mar',
#         4: 'Apr',
#         5: 'May',
#         6: 'Jun',
#         7: 'Jul',
#         8: 'Aug',
#         9: 'Sep',
#         10: 'Oct',
#         11: 'Nov',
#         12: 'Dec'
#     }

#     # Get all the SubjectInstances where the current user is assigned as a lecturer
#     subject_instances_objects = SubjectInstance.objects.all()
#     subject_instances_list = []

#     for subject_instance in subject_instances_objects:
#         subject = subject_instance.subject
#         start_date = subject_instance.start_date
#         end_date = subject_instance.start_date + \
#             timedelta(weeks=12) + timedelta(days=-2)
#         end_month = end_date.month

#         years.add(subject_instance.start_date.year)
#         if end_date.year > start_date.year:
#             years.add(end_date.year)

#         # Add the subject instance to the list
#         subject_instances_list.append({
#             'subject_id': subject.subject_id,
#             'subject_name': subject.subject_name,
#             'start_year': start_date.year,
#             'start_month': start_date.month,
#             'instance_id': subject_instance.instance_id,
#             # 3-month range
#             'end_month': end_month,
#         })

#     # # Prepare subjects and active months
#     # for subject_instance in subject_instances:

#     years = sorted(list(years))

#     # Cache the result for this user for 10 minutes
#     cache.set('instance_data', (years, months, subject_instances_list), 600)

#     return years, months, subject_instances_list


def get_overloaded_lecturers_and_instances():
    # Filter for overloaded workloads directly using the is_overloaded boolean
    overloaded_workloads = LecturerWorkload.objects.filter(is_overloaded=True)
    lecturer_workload_dict = {}

    for workload in overloaded_workloads:
        lecturer = workload.user_profile
        month = workload.month
        year = workload.year
        # Calculate workload percentage using the existing function
        workload_percentage = lecturer.workload_percentage_for_month(month, year)
        month_year_key = f'{month}/{year}'

        print(f"Processing overloaded workload for {lecturer.first_name} {lecturer.last_name} in {month_year_key} with percentage: {workload_percentage}%")

        # Initialize the lecturer's entry in the dictionary if it doesn't exist
        if lecturer not in lecturer_workload_dict:
            lecturer_workload_dict[lecturer] = {}

        # Find all subject instances where the lecturer is assigned in the overloaded month/year
        subject_instances = SubjectInstance.objects.filter(
            subjectinstancelecturer__user=lecturer,
            start_date__month=month,
            start_date__year=year
        )
        print(f"Subject instances for {lecturer.first_name} in {month_year_key}: {subject_instances}")

        # Store both the workload_percentage and subject instances in a nested dictionary
        lecturer_workload_dict[lecturer][month_year_key] = {
            'workload_percentage': workload_percentage,
            'subject_instances': list(subject_instances)
        }

    print("Final lecturer workload dict:", lecturer_workload_dict)
    return lecturer_workload_dict



def overloaded_lecturers(request):
    lecturer_workload_dict = get_overloaded_lecturers_and_instances()
    print("overloaded_lecturers view:", lecturer_workload_dict)
    # Render the modal template, passing the lecturer workload dictionary
    return render(request, 'overloaded_lecturers.html', {
        'lecturer_workload_dict': lecturer_workload_dict
    })
