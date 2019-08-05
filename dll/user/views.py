from django.contrib.auth import login, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView, FormView

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
        return ctx


class ProfileView(TemplateView):
    template_name = 'dll/user/profile.html'


class SignUpView(FormView):
    template_name = 'dll/user/signup.html'
    form_class = SignUpForm
    email_template = 'dll/user/email/account_activation_email.html'

    def form_valid(self, form):
        user = form.save(commit=False)  # TODO: should the user be active without confirming his email?
        # user.is_active = False
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
        return redirect('user:profile')


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
        return redirect('user:profile')
    else:
        return render(request, 'dll/user/account_activation_invalid.html')
