from django.urls import path
from . import views

# app_name = 'site_admin'

urlpatterns = [
    # path('subjects/', views.subject_list, name='subject_list'),
    path('user_management/', views.user_management, name='user_management'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('set_expertise/<int:user_id>/', views.set_expertise, name='set_expertise'),
    path('add_user/', views.add_user, name='add_user'),
    # path('add_user/', views.add_user, name='add_user'),
    # path('update_user/<int:user_id>/', views.update_user, name='update_user'),
    path('user_list/', views.user_list, name='user_list'),
    # path('select-user/', views.select_user, name='select_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('message_modal/', views.message_modal, name='message_modal'),
    path('confirm_delete_user/<int:user_id>/', views.confirm_delete_user, name='confirm_delete_user'),
]
