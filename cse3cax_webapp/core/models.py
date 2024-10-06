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

    class Meta:
        db_table = 'user_profile'
        managed = True


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


class SubjectInstanceLecturer(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    subject_instance = models.ForeignKey(
        SubjectInstance, on_delete=models.CASCADE)

    class Meta:
        db_table = 'subject_instance_lecturer'
