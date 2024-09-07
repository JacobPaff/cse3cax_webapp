from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from admin_user_input.models import UserProfile, Subject
from admin_user_input.forms import UserProfileForm
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.http import HttpResponse


def home(request):
    return render(request, 'home.html')


def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'subject_list.html', {'subjects': subjects})


def user_management(request, user_id=None):
    selected_user = get_object_or_404(UserProfile, user_id=user_id) if user_id else None
    users = UserProfile.objects.all() 
    form = UserProfileForm(instance=selected_user)
    context = {
        'form': form,
        'users':users,
        'selected_user': selected_user,
    }
    return render(request, 'user_management.html', context)

def user_list(request):
    users = UserProfile.objects.all()
    return render(request, 'user_list.html', {'users': users})

# def add_user(request):
#     if request.method == 'POST':
#         form = UserProfileForm(request.POST)
#         if form.is_valid():
#             form.save()
#             form = UserProfileForm()  # Reset the form after saving
#     else:
#         form = UserProfileForm()
#     return render(request, 'user_form.html', {'form': form})

# def update_user(request, user_id):
#     user_profile = get_object_or_404(UserProfile, user_id=user_id)
#     if request.method == 'POST':
#         form = UserProfileForm(request.POST, instance=user_profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'User updated successfully!')
#             return redirect('user_list')
#     else:
#         form = UserProfileForm(instance=user_profile)
#     return render(request, 'user_form.html', {'form': form, 'user': user_profile})

@require_http_methods(["POST"])
def select_user(request):
    user_id = request.POST.get('user_id')
    selected_user = get_object_or_404(UserProfile, user_id=user_id)
    form = UserProfileForm(instance=selected_user)
    context = {
        'form': form,
        'selected_user': selected_user
    }
    
    return render(request, 'user_form.html', context)



@require_http_methods(["DELETE"])
@csrf_protect
def delete_user(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully')
    html = render_to_string('user_form.html', {'form': UserProfileForm()}, request=request)
                # Create response with the rendered HTML
    response = HttpResponse(html)
    response['HX-Trigger'] = 'refreshUserList'
    return response
    # return HttpResponse("<div id='user-form'>User deleted successfully!</div>")


# @require_http_methods(["GET", "POST"])
# def update_user(request, user_id):
#     user = get_object_or_404(UserProfile, user_id=user_id)
#     if request.method == "POST":
#         form = UserProfileForm(request.POST, instance=user)
#         if form.is_valid():
#             form.save()
#             return HttpResponse("<div id='user-form'>User updated successfully!</div>")
#     else:
#         form = UserProfileForm(instance=user)
#     return render(request, 'update_user.html', {'form': form, 'user': user})

@require_http_methods(["GET", "POST"])
def update_user(request, user_id):
    user = get_object_or_404(UserProfile, user_id=user_id)
    
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully')
            html = render_to_string('user_form.html', {
                'form': UserProfileForm(instance=user),
                'selected_user': user
            }, request=request)
                        # Create response with the rendered HTML
            response = HttpResponse(html)
            response['HX-Trigger'] = 'refreshUserList'
            return response
        else:
            # If form is invalid, return the form with validation errors
            return render(request, 'user_form.html', {'form': form, 'selected_user': user})
    else:
        # Load the form with the user's current data for editing
        form = UserProfileForm(instance=user)
    return render(request, 'user_form.html', {'form': form, 'selected_user': user})



def add_user(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User added successfully')
            html = render_to_string('user_form.html', {
                'form': UserProfileForm(),
            }, request=request)
                        # Create response with the rendered HTML
            response = HttpResponse(html)
            response['HX-Trigger'] = 'refreshUserList'
            return response
        else:
            # If the form is invalid, return the form with errors and retain entered data
            return render(request, 'user_form.html', {'form': form, 'selected_user': None})
    else:
        # Initial form load
        form = UserProfileForm()
    return render(request, 'user_form.html', {'form': form, 'selected_user': None})


# MODALS
def message_modal(request):
    title = request.GET.get('title', 'Message')
    message = request.GET.get('message', '')
    return render(request, 'modals/message_modal.html', {'title': title, 'message': message})

def confirm_delete_modal(request):
    item_type = request.GET.get('item_type', 'item')
    delete_url = request.GET.get('delete_url', '')
    hx_target = request.GET.get('hx_target', '')
    return render(request, 'modals/confirm_delete_modal.html', {
        'item_type': item_type,
        'delete_url': delete_url,
        'hx_target': hx_target
    })


