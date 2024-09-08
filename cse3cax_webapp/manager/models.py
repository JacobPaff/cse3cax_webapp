from django.db import models
from core.models import Subject, UserProfile

class SubjectInstance(models.Model):
    instance_id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(
        Subject, on_delete=models.DO_NOTHING, blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    users = models.ManyToManyField(
        UserProfile, related_name='subject_instances', blank=True)
    start_date = models.DateField(blank=True, null=True)
    enrollments = models.IntegerField(blank=True, null=True)