from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('add_user/', views.add_user, name='add_user'),
    path('user_management/', views.user_management, name='user_management'),
]

