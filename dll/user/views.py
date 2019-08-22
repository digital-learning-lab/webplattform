import json

from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView, FormView

from dll.content.models import Content, TeachingModule
from dll.content.serializers import TeachingModuleSerializer
from dll.content.views import BreadcrumbMixin
from dll.general.utils import GERMAN_STATES
from dll.user.tokens import account_activation_token
from .forms import SignUpForm


USER_MODEL = get_user_model()


class TestView(TemplateView):
    template_name = 'dll/test.html'

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user', None)
        if user_id:
            user = USER_MODEL.objects.get(pk=user_id)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return super(TestView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(TestView, self).get_context_data(**kwargs)
        ctx['users'] = USER_MODEL.objects.all()
        ctx['teaching_modules'] = Content.objects.teaching_modules()
        ctx['tools'] = Content.objects.tools()
        ctx['trends'] = Content.objects.trends()
        return ctx




class MyContentView(TemplateView, BreadcrumbMixin):
    template_name = 'dll/user/content/overview.html'
    breadcrumb_title = 'Meine Inhalte'
    breadcrumb_url = reverse_lazy('user-content-overview')

    def get_context_data(self, **kwargs):
        ctx = super(MyContentView, self).get_context_data(**kwargs)
        ctx['contents'] = self.request.user.qs_any_content()
        return ctx


class CreateEditTeachingModule(TemplateView, BreadcrumbMixin):
    template_name = 'dll/user/content/add_teaching_module.html'
    breadcrumb_title = 'Digitalen Unterrichtsbaustein {}'
    breadcrumb_url = reverse_lazy('add-teaching-module')

    def get_context_data(self, **kwargs):
        ctx = super(CreateEditTeachingModule, self).get_context_data(**kwargs)
        slug = self.kwargs.get('slug', None)
        if slug:
            obj = self.get_object()
            ctx['obj'] = json.dumps(TeachingModuleSerializer(obj).data)
        return ctx

    def get_object(self):
        if not getattr(self, 'object', None):
            slug = self.kwargs.get('slug', None)
            if slug:
                self.object = get_object_or_404(TeachingModule, slug=slug)
        return getattr(self, 'object', None)


    def get_breadcrumbs(self):
        bcs = super(CreateEditTeachingModule, self).get_breadcrumbs()
        temp_bc = bcs[1]
        del bcs[1]
        if self.get_object():
            temp_bc['title'] = temp_bc['title'].format('bearbeiten')
        else:
            temp_bc['title'] = temp_bc['title'].format('erstellen')
        bcs.extend([
            {'title': 'Meine Inhalte', 'url': reverse_lazy('user-content-overview')},
            temp_bc
        ])
        return bcs


class SignUpView(FormView):
    template_name = 'dll/user/signup.html'
    form_class = SignUpForm
    email_template = 'dll/user/email/account_activation_email.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        current_site = get_current_site(self.request)
        subject = 'Activate Your MySite Account'
        message = render_to_string(self.email_template, {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        user.email_user(subject, message)
        return redirect('home')


def activate_user(request, uidb64, token, backend='django.contrib.auth.backends.ModelBackend'):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = USER_MODEL.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, USER_MODEL.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.doi_confirmed = True
        user.save()
        login(request, user, backend=backend)
        return redirect('user-content-overview')
    else:
        return render(request, 'dll/user/account_activation_invalid.html')
