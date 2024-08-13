from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('user_management/', views.user_management, name='user_management'),
    path('add_user/', views.add_user, name='add_user'),
    path('update_user/<int:user_id>/', views.update_user, name='update_user'),
    path('user_list/', views.user_list, name='user_list'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
]