from django.urls import path, re_path, reverse_lazy
from django.contrib.auth import views as auth_views

from .views import SignUpView, ProfileView, activate_user

app_name = 'user'

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='dll/user/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
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
