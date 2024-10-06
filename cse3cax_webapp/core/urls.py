from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_redirect, name='login_redirect'),
    path('cognito_callback/', views.cognito_callback, name='cognito_callback'),
    path('logout/', views.logout_view, name='logout'),
]