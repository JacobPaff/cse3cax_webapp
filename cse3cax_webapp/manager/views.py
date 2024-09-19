from django.shortcuts import render, get_object_or_404
from core.models import SubjectInstance, Subject, SubjectInstanceLecturer, UserProfile
from .forms import SubjectInstanceForm
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q


def subject_instances(request):
    subjects = Subject.objects.all()
    return render(request, 'subject_instances.html', {'subjects': subjects})


def instance_list(request):
    # subject = request.GET.get('subject')
    query = request.GET.get('search', '')
    subject_instances = SubjectInstance.objects.all()
    if query:
        subject_instances = subject_instances.filter(
            Q(subject__subject_name__icontains=query) |
            Q(subject__subject_id__icontains=query)
        )
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
    subject_instance = get_object_or_404(
        SubjectInstance, instance_id=instance_id)
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
    delete_url = reverse("delete_instance", kwargs={
                         "instance_id": instance.instance_id})
    hx_post_attribute = f'hx-post="{delete_url}"'
    context = {
        'form_string': form_string,
        'hx_post_attribute': hx_post_attribute,
    }
    return render(request, 'modals/confirm_delete_modal.html', context)


def delete_instance(request, instance_id):
    subject_instance = get_object_or_404(
        SubjectInstance, instance_id=instance_id)
    subject_instance.delete()
    # No content response
    return HttpResponse(status=204, headers={'Hx-Trigger': 'instanceListChanged'})


def assign_lecturer_instance(request):
    instance_id = request.GET.get('instance_id')
    return render(request, 'assign_lecturer_instance.html', {'instance_id': instance_id})


def lecturer_list(request):
    query = request.GET.get('search', '')
    instance_id = request.GET.get('instance_id')

    # Get the subject instance
    subject_instance = SubjectInstance.objects.get(pk=instance_id)

    # Get lecturers assigned to the subject instance
    assigned_lecturers = UserProfile.objects.filter(
        subjectinstancelecturer__subject_instance=instance_id)
    # assigned_lecturers = UserProfile.objects.all()
    # Get lecturers who have expertise in the subject of this instance
    expertised_lecturers = UserProfile.objects.filter(
        lecturerexpertise__subject=subject_instance.subject
    )
    # expertised_lecturers = UserProfile.objects.all()

    # Combine both filters: lecturers with expertise and assigned to the subject instance
    user_list = expertised_lecturers

    # Can this .... for now
    # Apply the search query to filter by first or last name
    if query:
        user_list = user_list.filter(
            Q(first_name__icontains=query) | Q(
                last_name__icontains=query)
        )

    return render(request, 'lecturer_list.html', {
        'user_list': user_list,
        'assigned_lecturers': assigned_lecturers
    })

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
