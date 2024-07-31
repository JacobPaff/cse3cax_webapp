from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from admin_user_input.models import Subject, UserProfile
from admin_user_input.forms import UserProfileForm


def home(request):
    return render(request, 'home.html')


def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'subject_list.html', {'subjects': subjects})


# def add_user(request):
#     if request.method == 'POST':
#         form = UserProfileForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('user_list')  # Redirect to a page where you can list users
#     else:
#         form = UserProfileForm()

#     return render(request, 'add_user.html', {'form': form})+
def add_user(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User profile added successfully!')
            return redirect('add_user')  # Redirect to the same page
    else:
        form = UserProfileForm()

    return render(request, 'add_user.html', {'form': form})


def user_management(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    else:
        form = UserProfileForm()

    users = UserProfile.objects.all()
    return render(request, 'user_management.html', {'form': form, 'users': users})
