from django.contrib.auth.decorators import login_required
from django.urls import path, re_path, reverse_lazy
from django.contrib.auth import views as auth_views

from dll.user.views import SignUpSuccessfulView
from .views import SignUpView, activate_user, ProfileViewIndex, ProfileViewEmails, ProfileViewChangePassword, \
    ProfileViewDelete, ProfileViewDeleteSuccess, confirm_email

app_name = 'user'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signup/confirm-email', SignUpSuccessfulView.as_view(), name='signup-success'),
    path('login/', auth_views.LoginView.as_view(template_name='dll/user/login.html'), name='login'),
    path('profil/', login_required(ProfileViewIndex.as_view()), name='profile'),
    path('profil/passwort-aendern/', login_required(ProfileViewChangePassword.as_view()), name='password_change'),
    path('profil/email/', login_required(ProfileViewEmails.as_view()), name='email'),
    re_path(r'^profil/email-bestaetigen/(?P<cr_idb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            confirm_email, name='email_confirm'),

    path('profil/loeschen/', login_required(ProfileViewDelete.as_view()), name='account_delete'),
    path('profil/loeschen/erfolgreich/', ProfileViewDeleteSuccess.as_view(), name='account_delete_success'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    re_path(r'^account-activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            activate_user, name='activate'),
    path('reset/',
         auth_views.PasswordResetView.as_view(
             template_name='dll/user/password_reset.html',
             email_template_name='dll/user/email/password_reset_email.html',
             subject_template_name='dll/user/email/password_reset_subject.txt',
             success_url=reverse_lazy('user:password_reset_done')
         ),
         name='password_reset'),
    path('reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='dll/user/password_reset_done.html'),
         name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.PasswordResetConfirmView.as_view(template_name='dll/user/password_reset_confirm.html'),
            name='password_reset_confirm'),
    path('reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='dll/user/password_reset_complete.html'),
         name='password_reset_complete'),
]
