# 
# Views for User Management and Lecturer Expertise
# =================================================
# This file defines the view functions for managing users, editing user profiles, 
# setting lecturer expertise, and handling user deletion within the application.
# It includes functionality for rendering modals, confirming actions, and updating lists dynamically.
#
# File: views.py
# Author: Jacob Paff
# Revisions:
#   - 17-09-24: Initial file created by Jacob Paff. Added views for user management, adding, and editing users.
#   - 25-09-24: Added lecturer expertise form handling and user deletion confirmation modal.
#

from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from core.models import UserProfile, Role
from django.http import HttpResponse
from site_admin.forms import UserProfileForm, LecturerExpertiseForm
from django.contrib.auth.decorators import user_passes_test

# Helper function to check if the user is an admin
def is_admin(user):
    return user.is_authenticated and (user.role.role_id == 'Administrator' or user.role.role_id == 'Testing')

# View to render the user management page
@user_passes_test(is_admin, login_url='login_redirect')
def user_management(request):
    roles = Role.objects.all()
    return render(request, 'user_management.html', {'roles': roles})

# View to edit an existing user
@user_passes_test(is_admin, login_url='login_redirect')
def edit_user(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204, headers={'Hx-Trigger': 'userListChanged'})
    else:
        form = UserProfileForm(instance=user)
    form_string = f'Edit {user.first_name} {user.last_name}'
    return render(request, 'modals/form_modal.html', {'form': form, 'form_string': form_string})

# View to add a new user
@user_passes_test(is_admin, login_url='login_redirect')
def add_user(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204, headers={'Hx-Trigger': 'userListChanged'})
    else:
        form = UserProfileForm()
    form_string = 'Add User'
    return render(request, 'modals/form_modal.html', {'form': form, 'form_string': form_string})

# View to confirm the deletion of a user
@user_passes_test(is_admin, login_url='login_redirect')
def confirm_delete_user(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)
    form_string = f'Are you sure you want to delete user {user.first_name} {user.last_name}?'
    delete_url = reverse("delete_user", kwargs={"user_id": user.user_id})
    hx_post_attribute = f'hx-post="{delete_url}"'
    context = {
        'form_string': form_string,
        'hx_post_attribute': hx_post_attribute,
    }
    return render(request, 'modals/confirm_delete_modal.html', context)

# View to delete a user and update related workload if needed
@user_passes_test(is_admin, login_url='login_redirect')
def delete_user(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)
    user.delete_user()  # Method handles workload recalculation
    return HttpResponse(status=204, headers={'Hx-Trigger': 'userListChanged'})

# View to list users, filtered by role if provided
@user_passes_test(is_admin, login_url='login_redirect')
def user_list(request):
    role = request.GET.get('role')
    users = UserProfile.objects.filter(role__role_id=role) if role else UserProfile.objects.all()
    return render(request, 'user_list.html', {'users': users})

# View to render message modals for dynamic messaging
def message_modal(request):
    title = request.GET.get('title', 'Message')
    message = request.GET.get('message', '')
    return render(request, 'modals/message_modal.html', {'title': title, 'message': message})

# View to set lecturer expertise
@user_passes_test(is_admin, login_url='login_redirect')
def set_expertise(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)
    if request.method == "POST":
        form = LecturerExpertiseForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204, headers={'Hx-Trigger': 'userListChanged'})
    else:
        form = LecturerExpertiseForm(user=user)
    form_string = f'Set Lecturer Expertise for {user.first_name} {user.last_name}'
    return render(request, 'modals/form_modal.html', {'form': form, 'form_string': form_string})
