from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import FormView

from dll.communication.forms import ContactForm, NewsletterForm
from dll.communication.models import NewsletterSubscrption
from dll.communication.tokens import newsletter_confirm_token
from dll.content.views import BreadcrumbMixin
from django.utils.translation import ugettext_lazy as _


class ContactView(FormView, BreadcrumbMixin):
    template_name = 'dll/contact.html'
    breadcrumb_title = 'Kontakt'
    breadcrumb_url = reverse_lazy('communication:contact')
    form_class = ContactForm
    success_url = reverse_lazy('faq')

    def post(self, request, *args, **kwargs):
        if settings.VALIDATE_RECAPTCHA:
            pass  # todo: build in recaptcha
        else:
            return super(ContactView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        # send_mail(event_type_code='')
        form.send_emails(self.request.user)
        return super(ContactView, self).form_valid(form)


class NewsletterRegisterView(FormView, BreadcrumbMixin):
    template_name = 'dll/newsletter/register.html'
    breadcrumb_title = 'Newsletteranmeldung'
    breadcrumb_url = reverse_lazy('communication:newsletter')
    form_class = NewsletterForm
    success_url = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        if settings.VALIDATE_RECAPTCHA:
            pass  # todo: build in recaptcha
        else:
            return super(NewsletterRegisterView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        subscription, created = NewsletterSubscrption.objects.update_or_create(
            email=form.cleaned_data['email_address'],
            defaults={
                'checked_text': None  # todo: save terms text?
            }
        )
        token = reverse('communication:newsletter-confirm', kwargs={
            'nl_id_b64': urlsafe_base64_encode(force_bytes(subscription.pk)),
            'token': newsletter_confirm_token.make_token(subscription)
        })
        token = self.request.build_absolute_uri(token)
        form.send_registration_email(token)
        messages.success(self.request, _('Bestätigungslink versendet. Sie erhalten in Kürze eine '
                                         'E-Mail, um die Newsletter-Anmeldung zu bestätigen.'))
        messages.success(self.request, "test")
        return super(NewsletterRegisterView, self).form_valid(form)


class NewsletterUnregisterView(FormView, BreadcrumbMixin):
    template_name = 'dll/newsletter/unregister.html'
    breadcrumb_title = 'Newsletterabmeldung'
    breadcrumb_url = reverse_lazy('communication:newsletter-unregister')
    form_class = NewsletterForm
    success_url = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        if settings.VALIDATE_RECAPTCHA:
            pass  # todo: build in recaptcha
        else:
            return super(NewsletterUnregisterView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            sub = NewsletterSubscrption.objects.get(email=form.cleaned_data['email_address'])
            sub.deactivate()
            form.send_unregister_email()
        except NewsletterSubscrption.DoesNotExist:
            # todo: add messages
            pass
        return super(NewsletterUnregisterView, self).form_valid(form)


def newsletter_registration_confirm(request, nl_id_b64, token):
    try:
        uid = force_text(urlsafe_base64_decode(nl_id_b64))
        subscription = NewsletterSubscrption.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, NewsletterSubscrption.DoesNotExist):
        subscription = None

    if subscription is not None and newsletter_confirm_token.check_token(subscription, token):
        subscription.activate()
        messages.success(request, _("Newsletter Anmeldung erfolgreich"))
    else:
        messages.error(request, _("Newsletter Anmeldung nicht erfolgreich. Versuchen Sie es erneut."))

    return redirect('home')
