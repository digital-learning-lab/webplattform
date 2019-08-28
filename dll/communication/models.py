import logging

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.sites.models import Site
from django.db import models
from django.template import Template, TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from django.utils.encoding import smart_text as u, force_bytes

from dll.communication.managers import CommunicationEventTypeManager
from dll.communication.tokens import co_author_invitation_token
from dll.content.models import Content
from dll.user.models import DllUser

logger = logging.getLogger('dll.communication.models')


class CommunicationEvent(TimeStampedModel):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               related_name="communication_events", verbose_name=_("Auslösender User"), null=True)
    from_email = models.CharField(max_length=128)
    to = ArrayField(models.EmailField())
    cc = ArrayField(models.EmailField(), null=True)
    bcc = ArrayField(models.EmailField(), null=True)
    event_type = models.ForeignKey('CommunicationEventType', on_delete=models.CASCADE, verbose_name=_("Event Type"))

    class Meta:
        verbose_name = _("Kommunikations-Ereignis")
        verbose_name_plural = _("Kommunikations-Ereignisse")
        ordering = ['-created']

    def __str__(self):
        recip = self.sender.id if self.sender else ''
        return _("'{type:s}' event for user #{number:s}").format(
            type=u(self.event_type.name),
            number=u(recip)
        )


class CommunicationEventType(TimeStampedModel):
    """
    A 'type' of communication.  Like a order confirmation email.
    """
    code = models.CharField(max_length=128, unique=True, editable=True,
                            help_text=_("Code, mit dem dieses Ereignis programmgesteuert gesucht werden kann."))

    #: Name is the friendly description of an event for use in the admin
    name = models.CharField(
        _('Name'), max_length=255,
        help_text=_("Dies dient nur zu organisatorischen Zwecken."))
    from_email = models.EmailField(max_length=128, default=settings.DEFAULT_FROM_EMAIL)
    # Template content for emails
    # NOTE: There's an intentional distinction between None and ''. None
    # instructs Oscar to look for a file-based template, '' is just an empty
    # template.
    email_subject_template = models.CharField(
        _('Email Subject Template'), max_length=255, blank=True, null=True)
    email_body_template = models.TextField(
        _('Email Body Template'), blank=True, null=True)
    email_body_html_template = models.TextField(
        _('Email Body HTML Template'), blank=True, null=True,
        help_text=_("HTML template"))

    # File templates
    email_subject_template_file = 'dll/communication/emails/%s/subject.txt'
    email_body_template_file = 'dll/communication/emails/%s/body.txt'
    email_body_html_template_file = 'dll/communication/emails/%s/body.html'

    objects = CommunicationEventTypeManager()

    class Meta:
        verbose_name = _("Art des Kommunikations-Ereignis")
        verbose_name_plural = _("Arten von Kommunikations-Ereignissen")

    def get_messages(self, ctx=None):
        """
        :param ctx: context for rendering template
        Return a dict of templates with the context merged in
        We look first at the field templates but fail over to
        a set of file templates that follow a conventional path.
        """

        # Build a dict of message name to Template instances
        templates = {'subject': 'email_subject_template',
                     'body': 'email_body_template',
                     # 'html': 'email_body_html_template'
                     }
        for name, attr_name in templates.items():
            field = getattr(self, attr_name, None)
            if field:
                # Template content is in a model field
                templates[name] = Template(field)
            else:
                # Model field is empty - look for a file template
                template_name = getattr(self, "%s_file" % attr_name) % self.code
                try:
                    templates[name] = get_template(template_name)
                except TemplateDoesNotExist:
                    templates[name] = None
                    logger.warning("Template file {path} missing for CommunicationEvent {code}"
                                   .format(path=template_name, code=self.code))

        # Pass base URL for serving images within HTML emails
        if ctx is None:
            ctx = {}
        ctx['static_base_url'] = getattr(
            settings, 'STATIC_URL', None)  # TODO set url here for images etc

        messages = {}
        for name, template in templates.items():
            messages[name] = template.render(ctx) if template else ''

        # fixme: subject passed in context is ignored

        # Ensure the email subject doesn't contain any newlines
        messages['subject'] = messages['subject'].replace("\n", "")
        messages['subject'] = messages['subject'].replace("\r", "")

        return messages

    def __str__(self):
        return self.name


class NewsletterSubscrption(TimeStampedModel):
    email = models.EmailField()
    doi_confirmed = models.BooleanField(default=False)
    doi_confirmed_date = models.DateTimeField(null=True, editable=False)
    checked_text = models.CharField(max_length=300, null=True, blank=True)

    def activate(self):
        self.doi_confirmed = True
        self.doi_confirmed_date = timezone.now()
        self.save()

    def deactivate(self):
        self.delete()


class CoAuthorshipInvitation(TimeStampedModel):
    by = models.ForeignKey(DllUser, on_delete=models.CASCADE, verbose_name=_("Einladung von"),
                           related_name='sent_invitations')
    to = models.ForeignKey(DllUser, on_delete=models.CASCADE, verbose_name=_("Einladung an"),
                           related_name='received_invitations')
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='invitations')
    accepted = models.BooleanField(null=True, verbose_name=_("Status"))
    message = models.TextField(max_length=500, verbose_name=_("Nachricht"), null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    def accept(self):
        self.accepted = True
        self.content.co_authors.add(self.to)
        self.send_invitation_accepted_mail()
        self.save()

    def decline(self):
        self.accepted = False
        self.send_invitation_declined_mail()
        self.save()

    def send_invitation_mail(self):
        from dll.communication.tasks import send_mail
        token = reverse('communication:coauthor-invitation', kwargs={
            'inv_id_b64': urlsafe_base64_encode(force_bytes(self.pk)),
            'token': co_author_invitation_token.make_token(self)
        })
        token = 'https://%s%s' % (Site.objects.get_current().domain, token)
        context = {
            'content_title': self.content.name,
            'content_type': self.content.type_verbose,
            'author': self.by.username,
            'invitee': self.to.username,
            'message': self.message,
            'token': token
        }
        send_mail.delay(
            event_type_code='COAUTHOR_INVITATION',
            ctx=context,
            sender_id=self.by.pk,
            recipient_ids=[self.to.pk]
        )

    def send_invitation_accepted_mail(self):
        from dll.communication.tasks import send_mail
        context = {
            'content_title': self.content.name,
            'message': self.message,
            'invited_user_name': self.to.full_name
        }
        send_mail.delay(
            event_type_code='COAUTHOR_INVITATION_ACCEPTED',
            ctx=context,
            sender_id=self.to.pk,
            recipient_ids=[self.by.pk]
        )

    def send_invitation_declined_mail(self):
        from dll.communication.tasks import send_mail
        context = {
            'content_title': self.content.name,
            'message': self.message,
            'invited_user_name': self.to.full_name
        }
        send_mail.delay(
            event_type_code='COAUTHOR_INVITATION_DECLINED',
            ctx=context,
            sender_id=self.to.pk,
            recipient_ids=[self.by.pk]
        )

    def __str__(self):
        return "Invitation by {by} to {to}".format(by=self.by.full_name, to=self.to.full_name )
