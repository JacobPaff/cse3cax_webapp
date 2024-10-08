from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from core.models import SubjectInstance, Subject, SubjectInstanceLecturer, UserProfile, WorkloadManager, LecturerExpertise
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
    subject_instance = get_object_or_404(SubjectInstance, instance_id=instance_id)
    if request.method == "POST":
        form = SubjectInstanceForm(request.POST, instance=subject_instance)
        if form.is_valid():
            # Get the student threshold
            student_threshold = WorkloadManager.STUDENT_THRESHOLD
            # Get the current enrollment count before saving the form
            current_enrollments = subject_instance.enrollments or 0  # Default to 0 if None         
            # Save the form to update the SubjectInstance
            form.save()
            # Get the updated enrollment count from the form data
            new_enrollments = form.cleaned_data.get('enrollments', 0)
            # Check if enrollments have changed and call update workload
            if current_enrollments > student_threshold or new_enrollments > student_threshold:
                subject_instance.update_lecturer_workload()                                                 #TODO: Deal with too much workload

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
    # ensure workload is recalculated on delete
    subject_instance.delete_and_update_workload()
    # No content response
    return HttpResponse(status=204, headers={'Hx-Trigger': 'instanceListChanged'})

# Assign Lecturers to Subject Instance Modal
@user_passes_test(is_manager, login_url='login_redirect')
def assign_lecturer_instance(request):
    instance_id = request.GET.get('instance_id')
    return render(request, 'assign_lecturer_instance.html', {'instance_id': instance_id})


@user_passes_test(is_manager, login_url='login_redirect')
@user_passes_test(is_manager, login_url='login_redirect')
def lecturer_list(request):
    query = request.GET.get('search', '')
    instance_id = request.GET.get('instance_id')

    # Get the subject instance
    subject_instance = SubjectInstance.objects.get(pk=instance_id)
    start_month = subject_instance.start_date.month
    year = subject_instance.start_date.year

    # Get lecturers assigned to the subject instance
    assigned_lecturers = UserProfile.objects.filter(
        subjectinstancelecturer__subject_instance=instance_id
    )

    # Get lecturers who have expertise in the subject of this instance
    expertised_lecturers = UserProfile.objects.filter(
        lecturerexpertise__subject=subject_instance.subject
    )

    # Combine both filters: lecturers with expertise and assigned to the subject instance
    lecturer_list = expertised_lecturers

    # Apply the search query to filter by first or last name
    if query:
        lecturer_list = lecturer_list.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

    # Create a list to store lecturers with their metadata for sorting
    lecturer_data = []

    # For each lecturer, find the maximum workload for the 3 months the instance is active
    for lecturer in lecturer_list:
        workload_percentages = [
            lecturer.workload_percentage_for_month(start_month, year),
            lecturer.workload_percentage_for_month(start_month + 1, year),
            lecturer.workload_percentage_for_month(start_month + 2, year)
        ]

        # Add max workload percentage to the lecturer object
        lecturer.max_workload_percent = max(workload_percentages)

        # Check if the lecturer is assigned to the instance
        is_assigned = assigned_lecturers.filter(pk=lecturer.pk).exists()

        # Count how many subjects this lecturer has expertise in
        expertise_count = LecturerExpertise.objects.filter(user=lecturer).count()

        # Store the lecturer and sorting info
        lecturer_data.append({
            'lecturer': lecturer,
            'is_assigned': is_assigned,
            'max_workload_percent': lecturer.max_workload_percent,
            'expertise_count': expertise_count,
        })

    # Sort the lecturers first by assigned (True first), then by max_workload_percent, then by expertise_count
    sorted_lecturers = sorted(
        lecturer_data,
        key=lambda x: (not x['is_assigned'], -x['max_workload_percent'], -x['expertise_count'])
    )

    # Pass only the sorted lecturers back to the template
    return render(request, 'lecturer_list.html', {
        'lecturer_list': [item['lecturer'] for item in sorted_lecturers],
        'assigned_lecturers': assigned_lecturers,
        'instance_id': instance_id,
    })


@user_passes_test(is_manager, login_url='login_redirect')
def add_lecturer_instance(request):
    instance_id = request.GET.get('instance_id')
    subject_instance = get_object_or_404(
        SubjectInstance, instance_id=instance_id)
    lecturer_id = request.GET.get('lecturer_id')
    lecturer = get_object_or_404(UserProfile, user_id=lecturer_id)
    # Add the lecturer to the subject instance lecturer and upates workload << Will return overworked lecturers TODO: Warn Overworked Lecturers
    subject_instance.add_lecturer(lecturer)
    # SubjectInstanceLecturer.objects.create(
    #     subject_instance=subject_instance, user=lecturer)
    return HttpResponse(status=201, headers={'Hx-Trigger': 'instanceLecturerChanged'})


@user_passes_test(is_manager, login_url='login_redirect')
def remove_lecturer_instance(request):
    instance_id = request.GET.get('instance_id')
    subject_instance = get_object_or_404(
        SubjectInstance, instance_id=instance_id)
    lecturer_id = request.GET.get('lecturer_id')
    lecturer = get_object_or_404(UserProfile, user_id=lecturer_id)
    # Remove the lecturer from the subject instance lecturer
    subject_instance.remove_lecturer(lecturer)                                              #TODO: Deal with too much workload
    # SubjectInstanceLecturer.objects.filter(
    #     subject_instance=subject_instance, user=lecturer).delete()
    return HttpResponse(status=201, headers={'Hx-Trigger': 'instanceLecturerChanged'})

def instance_calendar(request):
    years, months, subject_instances_list = all_instances_info()
    print(len(subject_instances_list))
    context = {
        'years': years,
        'months': months,
        # A dictionary with subjects and their active months
        'subject_instances_list': subject_instances_list,
    }
    # lecturers' : subject_instance.lecturer.all(),
    return render(request, 'instance_calendar.html', context)

@user_passes_test(is_manager, login_url='login_redirect')
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
        end_date = subject_instance.start_date + timedelta(weeks=12) + timedelta(days=-2)
        end_month = end_date.month

        years.add(subject_instance.start_date.year)
        if end_date.year > start_date.year:
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
