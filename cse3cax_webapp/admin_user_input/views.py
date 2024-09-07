from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from admin_user_input.models import UserProfile
from django.http import HttpResponse
from admin_user_input.forms import UserProfileForm, LecturerExpertiseForm


def home(request):
    return render(request, 'home.html')


def user_management(request):
    return render(request, 'user_management.html')


def edit_user(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204, headers={'Hx-Trigger':'userListChanged'})  # no content
    else:
        # Load the form with the user's current data for editing
        form = UserProfileForm(instance=user)
    return render(request, 'user_form.html', {'form': form, 'user_id': user.user_id})


def add_user(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204, headers={'Hx-Trigger':'userListChanged'})  # no content
    else:
        form = UserProfileForm()
    return render(request, 'user_form.html', {'form': form})


def confirm_delete_modal(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)
    return render(request, 'modals/confirm_delete_modal.html', {'user': user})

def user_list(request):
    users = UserProfile.objects.all()
    return render(request, 'user_list.html', {'users': users})

def delete_user(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)
    user.delete()
    return HttpResponse(status=204, headers={'Hx-Trigger':'userListChanged'})  # No content response


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
            return HttpResponse(status=204, headers={'Hx-Trigger':'userListChanged'})  # no content
    else:
        # Load the form with the user's current data for editing
        form = LecturerExpertiseForm(user=user)
    return render(request, 'set_expertise.html', {'form': form, 'user': user})
