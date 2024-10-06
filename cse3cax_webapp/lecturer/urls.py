from django.urls import path
from . import views

urlpatterns = [
    path('lecturer_roster', views.lecturer_roster, name='lecturer_roster'),
    path('lecturer_instance_list', views.lecturer_instance_list, name='lecturer_instance_list'),
    path('subject_instance_info/', views.subject_instance_info, name='subject_instance_info'),
]
