from django.shortcuts import get_object_or_404, render
from datetime import timedelta
from core.models import SubjectInstanceLecturer, SubjectInstance, Subject
from collections import defaultdict
from django.contrib.auth.decorators import user_passes_test

def is_lecturer(user):
    return user.is_authenticated and (user.role.role_id == 'Lecturer' or user.role.role_id == 'Testing') 

@user_passes_test(is_lecturer, login_url='login_redirect')
def lecturer_instance_list(request):
    # Define years and months for the table
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

    # Get the current logged-in user
    current_user = request.user
    # Get all the SubjectInstances where the current user is assigned as a lecturer
    subject_instances_objects = SubjectInstanceLecturer.objects.filter(
        user_id=current_user.pk).select_related('subject_instance', 'subject_instance__subject')
    subject_instances_list = []

    for subject_instances_object in subject_instances_objects:
        subject_instance = subject_instances_object.subject_instance
        subject = subject_instance.subject
        start_date = subject_instance.start_date
        # end_month = (subject_instance.start_date + timedelta(weeks=12)).month
        years.add(subject_instance.start_date.year)

        # # Create a dictionary indicating if each month is active
        # is_active_months = {
        #     month: (start_date.month <= month <= end_month) for month in months.keys()}

        # Add the subject instance to the list
        subject_instances_list.append({
            'subject_id': subject.subject_id,
            'subject_name': subject.subject_name,
            'start_year': start_date.year,
            'start_month': start_date.month,
            'instance_id': subject_instance.instance_id,
            # 3-month range
            # 'is_active_months': is_active_months
        })

    # # Prepare subjects and active months
    # for subject_instance in subject_instances:

    years = sorted(list(years))

    # Pass the necessary context to the template
    context = {
        'years': years,
        'months': months,
        # A dictionary with subjects and their active months
        'subject_instances_list': subject_instances_list,
    }
    return render(request, 'lecturer_instance_list.html', context)


def lecturer_roster(request):
    return render(request, 'lecturer_roster.html')


def subject_instance_info(request):
    instance_id = request.GET.get('instance_id')
    subject_instance = get_object_or_404(
        SubjectInstance, instance_id=instance_id)
    context = {
        'subject_instance': subject_instance,
        'end_date': subject_instance.start_date + timedelta(weeks=12),
        'lecturers' : subject_instance.lecturer.all(),
        'subject_name': subject_instance.subject.subject_name
    }
    return render(request, 'subject_instance_info.html', context)
