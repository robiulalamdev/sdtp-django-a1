from django.urls import path
from users.views import sign_up, sign_in, sign_out, activate_user, admin_dashboard, create_group, assign_role, delete_user, add_participants, delete_group, remove_participant, organizer_dashboard, participant_dashboard, rsvp_event, CustomLoginView, ProfileView, ChangePassword, CustomPasswordResetView, CustomPasswordResetConfirmView, EditProfileView
from django.contrib.auth.views import LogoutView, PasswordChangeDoneView


urlpatterns = [
    path('sign-up/', sign_up, name='sign-up'),
    # path('sign-in/', sign_in, name='sign-in'),
    path('sign-in/', CustomLoginView.as_view(), name='sign-in'),
    # path('sign-out/', sign_out, name='logout'),
    path('sign-out/', LogoutView.as_view(), name='logout'),

    path('activate/<int:user_id>/<str:token>/', activate_user),
    path('admin/dashboard/', admin_dashboard, name='admin-dashboard'),
    path('admin/create-group/', create_group, name='create-group'),
    path('admin/<int:user_id>/assign-role/', assign_role, name='assign-role'),
    path('admin/delete-user/<int:user_id>/', delete_user, name='delete-user'),
    path('admin/add-participants/<int:event_id>/', add_participants, name='add-participants'),
    path('admin/delete-participants/<int:event_id>/<int:user_id>/', remove_participant, name='delete-participant'),

    # for groups
    path('admin/delete-group/<int:group_id>/', delete_group, name='delete-group'),

    # for Organizer
    path('organizer/dashboard/', organizer_dashboard, name='organizer-dashboard'),

    # for Organizer
    path('participant/dashboard/', participant_dashboard, name='participant-dashboard'),

    # others
    path('rsvp/<int:event_id>/', rsvp_event, name='rsvp_event'),


    path('profile/', ProfileView.as_view(), name='profile'),
    path('password-change/', ChangePassword.as_view(), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'), name='password_change_done'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/<uidb64>/<token>/',
         CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('edit-profile/', EditProfileView.as_view(), name='edit_profile')
]
