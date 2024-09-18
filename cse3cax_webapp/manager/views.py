from django.shortcuts import render, get_object_or_404
from core.models import SubjectInstance,Subject
from .forms import SubjectInstanceForm
from django.http import HttpResponse
from django.urls import reverse

def subject_instances(request):
    subjects = Subject.objects.all()
    return render(request, 'subject_instances.html', {'subjects': subjects})


def instance_list(request):
    subject = request.GET.get('subject')
    if subject:
        subject_instances = SubjectInstance.objects.filter(subject__subject_id=subject)
    else:
        subject_instances = SubjectInstance.objects.all()
    return render(request, 'instance_list.html', {'subject_instances': subject_instances})


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

def edit_subject_instance(request, instance_id):
    subject_instance = get_object_or_404(SubjectInstance, instance_id=instance_id)
    if request.method == "POST":
        form = SubjectInstanceForm(request.POST, instance=subject_instance)
        if form.is_valid():
            form.save()
            return HttpResponse(status=204, headers={'Hx-Trigger': 'instanceListChanged'})
    else:
        form = SubjectInstanceForm(instance=subject_instance)
    form_string = 'Edit Subject Instance'
    return render(request, 'modals/form_modal.html', {'form': form, 'form_string': form_string})

def confirm_delete_instance(request, instance_id):
    instance = get_object_or_404(SubjectInstance, instance_id=instance_id)
    form_string = f'Are you sure you want to delete instance {instance.subject}-{instance.month}/{instance.year}?'
    delete_url = reverse("delete_instance", kwargs={"instance_id": instance.instance_id})
    hx_post_attribute = f'hx-post="{delete_url}"'
    context = {
        'form_string': form_string,
        'hx_post_attribute': hx_post_attribute,
    }
    return render(request, 'modals/confirm_delete_modal.html', context)

def delete_instance(request, instance_id):
    subject_instance = get_object_or_404(SubjectInstance, instance_id=instance_id)
    subject_instance.delete()
    return HttpResponse(status=204, headers={'Hx-Trigger':'instanceListChanged'})  # No content response

# def confirm_delete_modal(request, user_id):
#     user = get_object_or_404(UserProfile, user_id=user_id)
#     return render(request, 'modals/confirm_delete_modal.html', {'user': user})

# def edit_user(request, user_id):
#     user = get_object_or_404(UserProfile, user_id=user_id)
#     if request.method == "POST":
#         form = UserProfileForm(request.POST, instance=user)
#         if form.is_valid():
#             form.save()
#             return HttpResponse(status=204, headers={'Hx-Trigger':'userListChanged'})  # no content
#     else:
#         # Load the form with the user's current data for editing
#         form = UserProfileForm(instance=user)
#     form_string = f'Edit {user.first_name } { user.last_name}'
#     return render(request, 'modals/form_modal.html', {'form': form, 'form_string': form_string})

