from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from core.models import UserProfile, Role
from django.http import HttpResponse
from site_admin.forms import UserProfileForm, LecturerExpertiseForm


def home(request):
    return render(request, 'home.html')


def user_management(request):
    roles = Role.objects.all()
    return render(request, 'user_management.html', {'roles': roles})


def edit_user(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # no content
            return HttpResponse(status=204, headers={'Hx-Trigger': 'userListChanged'})
    else:
        # Load the form with the user's current data for editing
        form = UserProfileForm(instance=user)
    form_string = f'Edit {user.first_name } { user.last_name}'
    return render(request, 'modals/form_modal.html', {'form': form, 'form_string': form_string})


def add_user(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            # no content
            return HttpResponse(status=204, headers={'Hx-Trigger': 'userListChanged'})
    else:
        form = UserProfileForm()
    form_string = 'Add User'
    return render(request, 'modals/form_modal.html', {'form': form, 'form_string': form_string})


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


def user_list(request):
    role = request.GET.get('role')
    if role:
        users = UserProfile.objects.filter(role__role_id=role)
    else:
        users = UserProfile.objects.all()
    return render(request, 'user_list.html', {'users': users})


def delete_user(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)
    user.delete()
    # No content response
    return HttpResponse(status=204, headers={'Hx-Trigger': 'userListChanged'})


def message_modal(request):
    title = request.GET.get('title', 'Message')
    message = request.GET.get('message', '')
    return render(request, 'modals/message_modal.html', {'title': title, 'message': message})


def set_expertise(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)
    if request.method == "POST":
        form = LecturerExpertiseForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            # no content
            return HttpResponse(status=204, headers={'Hx-Trigger': 'userListChanged'})
    else:
        # Load the form with the user's current data for editing
        form = LecturerExpertiseForm(user=user)
    form_string = f'Set Lecturer Expertise for {user.first_name } { user.last_name}'
    return render(request, 'modals/form_modal.html', {'form': form, 'form_string': form_string})
