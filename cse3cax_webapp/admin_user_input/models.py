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
        db_table = 'UserProfile'
        managed = True

class Role(models.Model):
    role_id = models.CharField(primary_key=True, max_length=255)
    role_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'role'
        managed = True

    def __str__(self):
        return self.role_name
    
class Subject(models.Model):
    subject_id = models.CharField(primary_key=True, max_length=7)
    subject_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'subject'
        managed = True

class SubjectInstance(models.Model):
    instance_id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING, blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    enrollments = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'subject_instance'
        managed = True
