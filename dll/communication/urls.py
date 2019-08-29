from django.contrib.auth.decorators import login_required
from django.urls import path, re_path

from .views import NewsletterRegisterView, NewsletterUnregisterView, ContactView, newsletter_registration_confirm, \
    CoAuthorInvitationConfirmView, ContactSuccessView

app_name = 'communication'

urlpatterns = [
    path('kontakt', ContactView.as_view(), name='contact'),
    path('kontakt', ContactView.as_view(), name='contact-form'), # todo: remove this. just for avoiding immense bug stacktraces from reverse error
    path('kontakt/vielen-dank', ContactSuccessView.as_view(), name='contact-success'),
    path('newsletter', NewsletterRegisterView.as_view(), name='newsletter'),
    path('newsletter/abmelden', NewsletterUnregisterView.as_view(), name='newsletter-unregister'),
    re_path(r'^newsletter-activate/(?P<nl_id_b64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            newsletter_registration_confirm, name='newsletter-confirm'),
    re_path(r'^einladung/(?P<inv_id_b64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            login_required(CoAuthorInvitationConfirmView.as_view()), name='coauthor-invitation'),
]
