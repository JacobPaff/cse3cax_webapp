from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from admin_user_input.models import UserProfile, Subject
from admin_user_input.forms import UserProfileForm
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse


def home(request):
    return render(request, 'home.html')


def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'subject_list.html', {'subjects': subjects})


def user_management(request, user_id=None):
    user_profile = get_object_or_404(UserProfile, user_id=user_id) if user_id else None
    users = UserProfile.objects.all() 
    form = UserProfileForm(instance=user_profile)
    context = {
        'form': form,
        'users':users,
        'user_profile': user_profile,
    }
    return render(request, 'user_management.html', context)

def user_list(request):
    users = UserProfile.objects.all()
    return render(request, 'user_list.html', {'users': users})

def add_user(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            form = UserProfileForm()  # Reset the form after saving
    else:
        form = UserProfileForm()
    return render(request, 'user_form.html', {'form': form})

def update_user(request, user_id):
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('user_list')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'user_form.html', {'form': form, 'user': user_profile})

# def add_user(request):
#     if request.method == 'POST':
#         form = UserProfileForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'User added successfully!')
#             return HttpResponse(
#                 '<div id="message-container"></div>',
#                 headers={'HX-Trigger': 'userAdded'}
#             )
#     else:
#         form = UserProfileForm()
    
#     return render(request, 'add_user.html', {'form': form})






@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)
    user.delete()
    return HttpResponse("<div id='user-form'>User deleted successfully!</div>")


@require_http_methods(["GET", "POST"])
def update_user(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return HttpResponse("<div id='user-form'>User updated successfully!</div>")
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'update_user.html', {'form': form, 'user': user})
