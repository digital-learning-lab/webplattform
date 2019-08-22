from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import FormView

from dll.communication.forms import ContactForm
from dll.content.views import BreadcrumbMixin


class ContactView(FormView, BreadcrumbMixin):
    template_name = 'dll/contact.html'
    breadcrumb_title = 'Kontakt'
    breadcrumb_url = reverse_lazy('contact')
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
