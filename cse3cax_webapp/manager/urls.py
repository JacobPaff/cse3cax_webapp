from django.urls import path
from . import views

# app_name = 'manager'

urlpatterns = [
    path('subject_instances/', views.subject_instances, name='subject_instances'),
    path('instance_list/', views.instance_list, name='instance_list'),
    path('add_subject_instance/', views.add_subject_instance,
         name='add_subject_instance'),
    path('edit_subject_instance/<int:instance_id>',
         views.edit_subject_instance, name='edit_subject_instance'),
    path('assign_lecturer_instance/', views.assign_lecturer_instance,
         name='assign_lecturer_instance'),
    path('lecturer_list/', views.lecturer_list, name='lecturer_list'),
    path('confirm_delete_instance/<int:instance_id>',
         views.confirm_delete_instance, name='confirm_delete_instance'),
    path('delete_instance/<int:instance_id>/',
         views.delete_instance, name='delete_instance'),
    path('add_lecturer_instance/', views.add_lecturer_instance,
         name='add_lecturer_instance'),
    path('remove_lecturer_instance/', views.remove_lecturer_instance,
         name='remove_lecturer_instance'),
]
