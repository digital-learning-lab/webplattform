from django.contrib.auth import login
from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView, FormView

from .models import DllUser


class TestView(TemplateView):
    template_name = 'dll/test.html'

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user', '1')
        user = DllUser.objects.get(pk=user_id)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return super(TestView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(TestView, self).get_context_data(**kwargs)
        ctx['users'] = DllUser.objects.all()
        return ctx
