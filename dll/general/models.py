import logging

from django.conf import settings
from django.db import models

from django.utils.translation import ugettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from django_extensions.db.models import TimeStampedModel
from filer.models import BaseImage

from .utils import custom_slugify


logger = logging.getLogger('dll.publisher')


class PublisherModelBase(TimeStampedModel):
    STATE_PUBLISHED = False
    STATE_DRAFT = True

    publisher_linked = models.OneToOneField(
        'self',
        related_name='publisher_draft',
        null=True,
        editable=False,
        on_delete=models.CASCADE)

    publisher_is_draft = models.BooleanField(
        default=STATE_DRAFT,
        editable=False,
        db_index=True
    )

    class Meta:
        abstract = True


class PublisherModel(PublisherModelBase):
    # objects = PublisherQuerySet.as_manager()

    class Meta:
        abstract = True
        permissions = (
            ('can_publish', 'Can publish'),
        )

    def publish(self):
        if not self.publisher_is_draft:
            logger.exception('Can only publish drafts')
            return
        else:
            logger.debug('Publish {} with pk {}'.format(self.__class__.__name__, self.pk))
            return


class DllSlugField(AutoSlugField):

    def slugify_function(self, value):
        return custom_slugify(value)


class NewsletterSubscription(TimeStampedModel):
    email = models.EmailField()
    confirmation_date = models.DateField()


class Message(TimeStampedModel):
    TYPE_CHOICES = (
        ('co_author_invitation', _('Koauthorenschaftsanfrage')),
        ('bsb_contact_mail', _('BSB Kontaktanfrage')),
        ('dll_contact_mail', _('DLL Kontaktanfrage'))
    )

    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=140)
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
