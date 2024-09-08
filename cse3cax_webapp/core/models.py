from django.db import models


class UserProfile(models.Model):
    user_id = models.AutoField(primary_key=True)
    role = models.ForeignKey('Role', on_delete=models.DO_NOTHING)
    email = models.CharField(unique=True, max_length=254)
    fte_percentage = models.FloatField(blank=True, null=True)
    honorific = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)

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
        unique_together = ('subject', 'user')  # Composite unique constraint on subject and user
        # No primary key field required, Django will handle this with unique_together

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.subject.subject_name}"