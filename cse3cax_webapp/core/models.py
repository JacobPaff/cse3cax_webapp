# 
# Models for University Rostering System
# ======================================
# This file defines the data models for managing users, workloads, subjects, roles, and their relationships 
# in the rostering system. The models handle everything from user profiles to workload management 
# based on lecturer assignments and student enrollments.
#
# File: models.py
# Author: Jacob Paff
# Revisions:
#   - 17-09-24: Initial models created by Jacob Paff.
#   - 18-09-24: Added workload calculation methods in WorkloadManager and LecturerWorkload models.
#   - 07-10-24: Updated methods to manage lecturer workloads when adding/removing users from SubjectInstance.
#

from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserProfileManager(BaseUserManager):
    """
    Custom manager for UserProfile. Handles the creation of users and superusers.
    """
    def create_user(self, email, role, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_unusable_password()  # Password not stored for authentication
        user.save(using=self._db)
        return user

    def create_superuser(self, email, role, password=None, **extra_fields):
        # Create a superuser (not fully implemented in this example)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, role, password, **extra_fields)


class UserProfile(AbstractBaseUser):
    """
    Represents a user in the system, including lecturers and admins.
    Stores key information such as role, email, and FTE percentage.
    """
    user_id = models.AutoField(primary_key=True)
    role = models.ForeignKey('Role', on_delete=models.DO_NOTHING)
    email = models.CharField(unique=True, max_length=254)
    fte_percentage = models.FloatField(blank=True, null=True)
    honorific = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    def calc_max_workload(self):
        """
        Calculate the maximum allowed workload based on FTE percentage.
        """
        max_workload = self.fte_percentage * WorkloadManager.FULL_TIME_UNITS
        return max_workload

    def workload_percentage_for_month(self, month, year):
        """
        Calculate the workload percentage for a specific month and year based on the lecturer's workload.
        """
        max_workload = self.calc_max_workload()
        try:
            workload = LecturerWorkload.objects.get(
                user_profile=self,
                month=month,
                year=year
            )
        except LecturerWorkload.DoesNotExist:
            return 0  # Return 0 if no workload record exists
        if max_workload > 0:
            workload_percent = (workload.workload_value / max_workload) * 100
        else:
            workload_percent = 0
        return round(workload_percent, 2)

    def delete_user(self):
        """
        Delete a user profile and update lecturer workloads if necessary.
        """
        subject_instances = []
        if self.role.role_id == 'Lecturer':
            subject_instances = SubjectInstance.objects.filter(lecturer=self)
        self.delete()
        if subject_instances:
            for subject_instance in subject_instances:
                subject_instance.update_lecturer_workload()

    class Meta:
        db_table = 'user_profile'
        managed = True


class WorkloadManager(models.Manager):
    """
    Manager for handling workload calculations based on subject instances, student counts, and lecturer assistance.
    """
    FULL_TIME_UNITS = 600  # Full-time workload in units
    SUBJECTS_FOR_FULL_TIME = 6
    WORKLOAD_PER_SUBJECT = FULL_TIME_UNITS / SUBJECTS_FOR_FULL_TIME
    STUDENT_THRESHOLD = 10
    WORKLOAD_PER_STUDENT = 2.0
    ADDITIONAL_LECTURER_ASSISTANCE = 0.4

    def calculate_effective_workload(self, lecturers_count):
        """
        Calculate the effective workload, applying diminishing returns if multiple lecturers are involved.
        """
        if lecturers_count <= 1:
            return 1
        return 1 / (1 + self.ADDITIONAL_LECTURER_ASSISTANCE * (lecturers_count - 1))

    def calculate_additional_workload(self, students_count):
        """
        Calculate additional workload based on student count.
        """
        if students_count > self.STUDENT_THRESHOLD:
            return (students_count - self.STUDENT_THRESHOLD) * self.WORKLOAD_PER_STUDENT
        return 0

    def update_workload(self, user_profile: UserProfile, month: int, year: int):
        """
        Update workload for a user based on their subject assignments in a given month and year.
        """
        subject_instances = SubjectInstance.objects.filter(
            lecturer=user_profile,
            start_date__year=year,
            start_date__month=month
        )
        total_workload = 0
        for subject_instance in subject_instances:
            lecturers_count = subject_instance.lecturer.count()
            students_count = subject_instance.enrollments or 0
            base_workload = self.WORKLOAD_PER_SUBJECT
            additional_workload = self.calculate_additional_workload(students_count)
            effective_workload = (base_workload + additional_workload) * self.calculate_effective_workload(lecturers_count)
            total_workload += effective_workload

        workload, created = LecturerWorkload.objects.get_or_create(
            user_profile=user_profile,
            month=month,
            year=year,
        )
        workload.workload_value = total_workload
        workload.save()
        return workload


class LecturerWorkload(models.Model):
    """
    Model representing a lecturer's workload for a specific month and year.
    """
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='workloads')
    month = models.IntegerField()  # Month (1-12)
    year = models.IntegerField()   # Year
    workload_value = models.IntegerField(blank=True, null=True)
    is_overloaded = models.BooleanField(default=False)

    objects = WorkloadManager()

    class Meta:
        unique_together = ('user_profile', 'month', 'year')
        db_table = 'workload'


class Role(models.Model):
    """
    Represents different roles (e.g., Admin, Manager, Lecturer) in the system.
    """
    role_id = models.CharField(primary_key=True, max_length=13)

    class Meta:
        db_table = 'role'
        managed = True

    def __str__(self):
        return self.role_id


class Subject(models.Model):
    """
    Represents a subject in the system, e.g., 'CS101'.
    """
    subject_id = models.CharField(primary_key=True, max_length=7)
    subject_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'subject'
        managed = True

    def __str__(self):
        return f"{self.subject_id} - {self.subject_name}"


class LecturerExpertise(models.Model):
    """
    Represents the expertise of lecturers in specific subjects.
    """
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)

    class Meta:
        db_table = 'lecturer_expertise'
        unique_together = ('subject', 'user')
        managed = True

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.subject.subject_name}"


class SubjectInstance(models.Model):
    """
    Represents an instance of a subject in the system, including lecturer assignments and enrollments.
    """
    instance_id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING, blank=True, null=True)
    lecturer = models.ManyToManyField(UserProfile, related_name='subject_instances', blank=True, through='SubjectInstanceLecturer')
    start_date = models.DateField(blank=True, null=True)
    enrollments = models.IntegerField(blank=True, default=0)

    class Meta:
        db_table = 'subject_instance'

    def __str__(self):
        return f"{self.subject.subject_id} - {self.start_date.month}/{self.start_date.year}"


    def delete_and_update_workload(self):
        """
        Delete this subject instance and update workloads for associated lecturers.
        """
        self.update_lecturer_workload()
        self.delete()

    def add_lecturer(self, user_profile):
        """
        Add a lecturer to this subject instance and update workloads.
        """
        SubjectInstanceLecturer.objects.create(subject_instance=self, user=user_profile)
        exceeded_workload_lecturers = self.update_lecturer_workload()
        return exceeded_workload_lecturers

    def remove_lecturer(self, user_profile):
        """
        Remove a lecturer from this subject instance and update workloads.
        """
        SubjectInstanceLecturer.objects.filter(subject_instance=self, user=user_profile).delete()
        exceeded_workload_lecturers = self.update_lecturer_workload(user_profile)
        return exceeded_workload_lecturers

    def update_enrollments(self, new_enrollment_count):
        """
        Update the enrollment count and adjust workloads if necessary.
        """
        current_enrollments = self.enrollments or 0
        self.enrollments = new_enrollment_count
        self.save()
        if current_enrollments > WorkloadManager.STUDENT_THRESHOLD or new_enrollment_count > WorkloadManager.STUDENT_THRESHOLD:
            self.update_lecturer_workload()

    def update_lecturer_workload(self, removed_lecturer=None):
        """
        Update workload for all lecturers in this subject instance, handling workload recalculations.
        """
        month = self.start_date.month
        year = self.start_date.year
        exceeded_workload_lecturers = False
        # exceeded_workload_lecturers = set() 
        lecturers = list(self.lecturer.all())
        if removed_lecturer:
            lecturers.append(removed_lecturer)
        for lecturer in lecturers:
            workload = LecturerWorkload.objects.update_workload(lecturer, month, year)
            max_workload = lecturer.calc_max_workload()
            # Determine if the lecturer is overloaded and update the is_overloaded field
            is_overloaded = workload.workload_value > max_workload
            workload.is_overloaded = is_overloaded
            workload.save()

            if is_overloaded:
                exceeded_workload_lecturers = True
                # exceeded_workload_lecturers.add(lecturer)
        return exceeded_workload_lecturers


class SubjectInstanceLecturer(models.Model):
    """
    Junction table linking lecturers to subject instances.
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    subject_instance = models.ForeignKey(SubjectInstance, on_delete=models.CASCADE)

    class Meta:
        db_table = 'subject_instance_lecturer'
