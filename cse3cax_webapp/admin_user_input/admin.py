from django.contrib import admin
from .models import UserProfile, Role, Subject, SubjectInstance

admin.site.register(UserProfile)
admin.site.register(Role)
admin.site.register(Subject)
admin.site.register(SubjectInstance)