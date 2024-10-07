from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from core.models import SubjectInstance, Subject, SubjectInstanceLecturer, UserProfile
from .forms import SubjectInstanceForm
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache


def is_manager(user):
    return user.is_authenticated and (user.role.role_id == 'Manager' or user.role.role_id == 'Testing')


@user_passes_test(is_manager, login_url='login_redirect')
def subject_instances(request):
    subjects = Subject.objects.all()
    return render(request, 'subject_instances.html', {'subjects': subjects})


@user_passes_test(is_manager, login_url='login_redirect')
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


@user_passes_test(is_manager, login_url='login_redirect')
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


@user_passes_test(is_manager, login_url='login_redirect')
def delete_instance(request, instance_id):
    subject_instance = get_object_or_404(
        SubjectInstance, instance_id=instance_id)
    subject_instance.delete()
    # No content response
    return HttpResponse(status=204, headers={'Hx-Trigger': 'instanceListChanged'})


@user_passes_test(is_manager, login_url='login_redirect')
def assign_lecturer_instance(request):
    instance_id = request.GET.get('instance_id')
    return render(request, 'assign_lecturer_instance.html', {'instance_id': instance_id})


@user_passes_test(is_manager, login_url='login_redirect')
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


@user_passes_test(is_manager, login_url='login_redirect')
def add_lecturer_instance(request):
    instance_id = request.GET.get('instance_id')
    subject_instance = get_object_or_404(
        SubjectInstance, instance_id=instance_id)
    lecturer_id = request.GET.get('lecturer_id')
    lecturer = get_object_or_404(UserProfile, user_id=lecturer_id)
    # Add the lecturer to the subject instance lecturer
    SubjectInstanceLecturer.objects.create(
        subject_instance=subject_instance, user=lecturer)
    return HttpResponse(status=201, headers={'Hx-Trigger': 'instanceLecturerChanged'})


@user_passes_test(is_manager, login_url='login_redirect')
def remove_lecturer_instance(request):
    instance_id = request.GET.get('instance_id')
    subject_instance = get_object_or_404(
        SubjectInstance, instance_id=instance_id)
    lecturer_id = request.GET.get('lecturer_id')
    lecturer = get_object_or_404(UserProfile, user_id=lecturer_id)
    # Remove the lecturer to the subject instance lecturer
    SubjectInstanceLecturer.objects.filter(
        subject_instance=subject_instance, user=lecturer).delete()
    return HttpResponse(status=201, headers={'Hx-Trigger': 'instanceLecturerChanged'})

def instance_calendar(request):
    years, months, subject_instances_list = all_instances_info()
    # Pass the necessary context to the template
    context = {
        'years': years,
        'months': months,
        # A dictionary with subjects and their active months
        'subject_instances_list': subject_instances_list,
    }
    # lecturers' : subject_instance.lecturer.all(),
    return render(request, 'instance_calendar.html', context)

def assign_roster(request):
    years = set()
    for subject_instance in SubjectInstance.objects.all():
        years.add(subject_instance.start_date.year)
    years, months, _ = all_instances_info()
    return render(request, 'assign_roster.html', {'years': years, 'months': months})


def all_instances_info():
    
    # Check if the data is already cached for this user
    cached_data = cache.get('instance_data')
    if cached_data:
        return cached_data
    
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

    # Get all the SubjectInstances where the current user is assigned as a lecturer
    subject_instances_objects = SubjectInstance.objects.all()
    subject_instances_list = []

    for subject_instance in subject_instances_objects:
        subject = subject_instance.subject
        start_date = subject_instance.start_date
        end_date = subject_instance.start_date + timedelta(weeks=12)
        end_month = end_date.month

        years.add(subject_instance.start_date.year)
        if end_date.month > start_date.month:
            years.add(end_date.year)

        # Add the subject instance to the list
        subject_instances_list.append({
            'subject_id': subject.subject_id,
            'subject_name': subject.subject_name,
            'start_year': start_date.year,
            'start_month': start_date.month,
            'instance_id': subject_instance.instance_id,
            # 3-month range
            'end_month': end_month,
        })

    # # Prepare subjects and active months
    # for subject_instance in subject_instances:

    years = sorted(list(years))

    # Cache the result for this user for 10 minutes
    cache.set('instance_data', (years, months, subject_instances_list), 600)

    return years, months, subject_instances_list


# @user_passes_test(is_lecturer, login_url='login_redirect')
# def lecturer_instance_list(request):
#     current_user = request.user
#     years, months, subject_instances_list = lecturer_instances_info(current_user)
#     # Pass the necessary context to the template
#     context = {
#         'years': years,
#         'months': months,
#         # A dictionary with subjects and their active months
#         'subject_instances_list': subject_instances_list,
#     }
#     return render(request, 'lecturer_instance_list.html', context)