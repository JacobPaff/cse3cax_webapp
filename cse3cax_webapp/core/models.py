from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserProfileManager(BaseUserManager):
    def create_user(self, email, role, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_unusable_password()  # Set unusable password <<<Not using Django password>>>
        user.save(using=self._db)
        return user

    # Not Implemented - retain for testing - will need a Django password stored
    def create_superuser(self, email, role, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, role, password, **extra_fields)


class UserProfile(AbstractBaseUser):
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
        # Check if the workload exceeds the maximum allowed for the lecturer
        max_workload = self.fte_percentage * WorkloadManager.FULL_TIME_UNITS
        return max_workload
    
    def workload_percentage_for_month(self, month, year):
        # Get the max workload for the lecturer
        max_workload = self.calc_max_workload()
        # Query the LecturerWorkload for this user, for the given month and year
        try:
            workload = LecturerWorkload.objects.get(
                user_profile=self,
                month=month,
                year=year
            )
        except LecturerWorkload.DoesNotExist:
            return 0  # Return 0 if there is no workload record for that month/year
        # Calculate the percentage of max workload
        if max_workload > 0:
            workload_percent = (workload.workload_value / max_workload) * 100
        else:
            workload_percent = 0  # Handle case where max_workload is zero
        return round(workload_percent, 2)  # Round to 2 decimal places for workload_percent
    
    def delete_user(self, user_profile):
        subject_instances = []
        if self.role.role_id == 'Lecturer':
            subject_instances = SubjectInstance.objects.filter(lecturer=user_profile)
        self.delete()
        if subject_instances:
            for subject_instance in subject_instances:
                subject_instance.update_lecturer_workload() 

    class Meta:
        db_table = 'user_profile'
        managed = True

class WorkloadManager(models.Manager):
        # Constants
    FULL_TIME_UNITS = 600  # Full workload in units
    SUBJECTS_FOR_FULL_TIME = 6  # 6 subjects for full-time
    WORKLOAD_PER_SUBJECT = FULL_TIME_UNITS / SUBJECTS_FOR_FULL_TIME  # Workload units per subject
    STUDENT_THRESHOLD = 10  # Threshold of 10 students before workload applies
    WORKLOAD_PER_STUDENT = 2.0  # 2 units per student above the threshold
    ADDITIONAL_LECTURER_ASSISTANCE = 0.4  # 40% of workload reduction for additional lecturers

    def calculate_effective_workload(self, lecturers_count):
        # Formula to apply diminishing returns based on the number of lecturers
        if lecturers_count <= 1:
            return 1  # Full workload if only 1 lecturer
        else:
            return 1 / (1 + self.ADDITIONAL_LECTURER_ASSISTANCE * (lecturers_count - 1))

    def calculate_additional_workload(self, students_count):
        # Additional workload from students if count exceeds threshold
        if students_count > self.STUDENT_THRESHOLD:
            additional_workload = (students_count - self.STUDENT_THRESHOLD) * self.WORKLOAD_PER_STUDENT
        else:
            additional_workload = 0  # No additional workload for students <= 10
        return additional_workload
    
    def update_workload(self, user_profile: UserProfile, month: int, year: int):
        
        # Get all subject instances the user is assigned to for this month and year
        subject_instances = SubjectInstance.objects.filter(
            lecturer=user_profile,
            start_date__year=year,
            start_date__month=month
        )

        total_workload = 0

        for subject_instance in subject_instances:
            lecturers_count = subject_instance.lecturer.count()
            students_count = subject_instance.enrollments or 0

            # Base workload per subject
            base_workload = self.WORKLOAD_PER_SUBJECT

            # Calculate additional workload from student count
            additional_workload = self.calculate_additional_workload(students_count)

            # Apply diminishing returns based on lecturer count
            effective_workload = (base_workload + additional_workload) * self.calculate_effective_workload(lecturers_count)

            total_workload += effective_workload

        # Create or update workload record for the user
        workload, created = LecturerWorkload.objects.get_or_create(
            user_profile=user_profile,
            month=month,
            year=year,
        )
        workload.workload_value = total_workload
        workload.save()

        return workload

class LecturerWorkload(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='workloads')
    month = models.IntegerField()  # Store month as an integer (1-12)
    year = models.IntegerField()   # Store year as an integer
    workload_value = models.IntegerField(blank=True, null=True)

    objects = WorkloadManager()
    
    class Meta:
        unique_together = ('user_profile', 'month', 'year')  # Ensures unique workload per user, per month
        db_table = 'workload'

class Role(models.Model):
    role_id = models.CharField(primary_key=True, max_length=13)

    class Meta:
        db_table = 'role'
        managed = True

    def __str__(self):
        return self.role_id

class Subject(models.Model):
    subject_id = models.CharField(primary_key=True, max_length=7)
    subject_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'subject'
        managed = True

    def __str__(self):
        return f"{self.subject_id} - {self.subject_name}"


class LecturerExpertise(models.Model):
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)

    class Meta:
        db_table = 'lecturer_expertise'
        managed = True
        # Composite unique constraint on subject and user
        unique_together = ('subject', 'user')
        # No primary key field required, Django will handle this with unique_together

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.subject.subject_name}"


class SubjectInstance(models.Model):
    instance_id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(
        Subject, on_delete=models.DO_NOTHING, blank=True, null=True)
    lecturer = models.ManyToManyField(
        UserProfile, related_name='subject_instances', blank=True, through='SubjectInstanceLecturer')
    start_date = models.DateField(blank=True, null=True)
    enrollments = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'subject_instance'

    def delete_and_update_workload(self):
        # Call the custom method to update workloads for all associated lecturers
        self.update_lecturer_workload()

        # Delete the SubjectInstance
        self.delete()

    def add_lecturer(self, user_profile):
        SubjectInstanceLecturer.objects.create(subject_instance=self, user=user_profile)
        exceeded_workload_lecturers = self.update_lecturer_workload()
        return exceeded_workload_lecturers

    def remove_lecturer(self, user_profile):
        SubjectInstanceLecturer.objects.filter(subject_instance=self, user=user_profile).delete()
        exceeded_workload_lecturers = self.update_lecturer_workload(user_profile)
        return exceeded_workload_lecturers

    def update_enrollments(self, new_enrollment_count):
        student_threshold = WorkloadManager.STUDENT_THRESHOLD
        # Check the current number of students (before update)
        current_enrollments = self.enrollments or 0  # Default to 0 if enrollments is None
        # Update the enrollments
        self.enrollments = new_enrollment_count
        self.save()
        if current_enrollments > student_threshold or new_enrollment_count > student_threshold:
            self.update_lecturer_workload()

    def update_lecturer_workload(self, removed_lecturer=None):
        month = self.start_date.month
        year = self.start_date.year
        exceeded_workload_lecturers = set() 
        # Loop through all lecturers associated with this SubjectInstance
        # Retrieve all lecturers associated with this SubjectInstance
        lecturers = list(self.lecturer.all())  # Convert queryset to list to add removed_lecturer
        # Add removed_lecturer to the list if it is not None
        if removed_lecturer:
            lecturers.append(removed_lecturer)
        for lecturer in lecturers:
            # Call the update_workload method for each lecturer
            workload = LecturerWorkload.objects.update_workload(lecturer, month, year)
            # Check if the workload exceeds the maximum allowed for the lecturer
            max_workload = lecturer.calc_max_workload()
            # Track lecturers whose workload exceeds the limit
            if workload.workload_value > max_workload:
                exceeded_workload_lecturers.add(lecturer)
        return exceeded_workload_lecturers

class SubjectInstanceLecturer(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    subject_instance = models.ForeignKey(
        SubjectInstance, on_delete=models.CASCADE)

    class Meta:
        db_table = 'subject_instance_lecturer'
