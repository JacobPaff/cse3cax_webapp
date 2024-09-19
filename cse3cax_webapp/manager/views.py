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
    # Get lecturers who have expertise in the subject of this instance
    expertised_lecturers = UserProfile.objects.filter(
        lecturerexpertise__subject=subject_instance.subject
    )
    # Combine both filters: lecturers with expertise and assigned to the subject instance
    user_list = expertised_lecturers

    # Apply the search query to filter by first or last name
    if query:
        user_list = user_list.filter(
            Q(first_name__icontains=query) | Q(
                last_name__icontains=query)
        )

    return render(request, 'lecturer_list.html', {
        'user_list': user_list,
        'assigned_lecturers': assigned_lecturers,
        'instance_id': instance_id
    })


def add_lecturer_instance(request):
    instance_id = request.GET.get('instance_id')
    subject_instance = get_object_or_404(
        SubjectInstance, instance_id=instance_id)
    lecturer_id = request.GET.get('lecturer_id')
    lecturer = get_object_or_404(UserProfile, user_id=lecturer_id)
    # Add the lecturer to the subject instance lecturer
    print('working here')
    SubjectInstanceLecturer.objects.create(
        subject_instance=subject_instance, user=lecturer)
    return HttpResponse(status=201, headers={'Hx-Trigger': 'instanceLecturerChanged'})

def remove_lecturer_instance(request):
    instance_id = request.GET.get('instance_id')
    subject_instance = get_object_or_404(
        SubjectInstance, instance_id=instance_id)
    lecturer_id = request.GET.get('lecturer_id')
    lecturer = get_object_or_404(UserProfile, user_id=lecturer_id)
    # Remove the lecturer to the subject instance lecturer
    SubjectInstanceLecturer.objects.filter(subject_instance=subject_instance, user=lecturer).delete()
    return HttpResponse(status=201, headers={'Hx-Trigger': 'instanceLecturerChanged'})