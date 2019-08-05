from django.urls import path

from .views import SignUpView

app_name = 'user'

urlpatterns = [
    path('signup', SignUpView.as_view(), name='signup')
]
