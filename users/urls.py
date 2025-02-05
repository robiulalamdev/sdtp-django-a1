from django.urls import path
from users.views import sign_up, sign_in, sign_out, activate_user, admin_dashboard, create_group, assign_role, delete_user, add_participants, delete_group, remove_participant
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('sign-up/', sign_up, name='sign-up'),
    path('sign-in/', sign_in, name='sign-in'),
    path('sign-out/', sign_out, name='logout'),
    path('activate/<int:user_id>/<str:token>/', activate_user),
    path('admin/dashboard/', admin_dashboard, name='admin-dashboard'),
    path('admin/create-group/', create_group, name='create-group'),
    path('admin/<int:user_id>/assign-role/', assign_role, name='assign-role'),
    path('admin/delete-user/<int:user_id>/', delete_user, name='delete-user'),
    path('admin/add-participants/<int:event_id>/', add_participants, name='add-participants'),
    path('admin/delete-participants/<int:event_id>/<int:user_id>/', remove_participant, name='delete-participant'),

    # for groups
    path('admin/delete-group/<int:group_id>/', delete_group, name='delete-group'),
]
