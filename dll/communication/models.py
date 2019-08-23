import logging

from django.conf import settings
from django.db import models
from django.template import Template, TemplateDoesNotExist, Context, engines
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from django.utils.encoding import smart_text as u

from dll.communication.managers import CommunicationEventTypeManager


logger = logging.getLogger('dll.communication.models')


class CommunicationEvent(TimeStampedModel):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                  related_name="communication_events_received", verbose_name=_("Empfänger"), null=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               related_name="communication_events_sent", verbose_name=_("Absender"), null=True)
    email = models.CharField(_('Email'), max_length=127, blank=True)
    event_type = models.ForeignKey('CommunicationEventType', on_delete=models.CASCADE, verbose_name=_("Event Type"))

    class Meta:
        verbose_name = _("Kommunikations-Ereignis")
        verbose_name_plural = _("Kommunikations-Ereignisse")
        ordering = ['-created']

    def __str__(self):
        recip = self.recipient.id if self.recipient else ''
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
                     'html': 'email_body_html_template'}
        for name, attr_name in templates.items():
            field = getattr(self, attr_name, None)
            if field is not None:
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


def get_template(template_name, using=None):
    """
    Loads and returns a template for the given name.

    Raises TemplateDoesNotExist if no such template exists.
    """
    chain = []
    engines = _engine_list(using)
    for engine in engines:
        try:
            return engine.get_template(template_name)
        except TemplateDoesNotExist as e:
            chain.append(e)

    raise TemplateDoesNotExist(template_name, chain=chain)


def _engine_list(using=None):
    return engines.all() if using is None else [engines[using]]
