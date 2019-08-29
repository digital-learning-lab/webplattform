import logging

from django.conf import settings
from django.db import models

from django.utils.translation import ugettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from django_extensions.db.models import TimeStampedModel

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
        on_delete=models.SET_NULL)

    publisher_is_draft = models.BooleanField(
        default=STATE_DRAFT,
        editable=False,
        db_index=True
    )

    class Meta:
        abstract = True

    @property
    def is_draft(self):
        return self.publisher_is_draft == self.STATE_DRAFT

    @property
    def is_public(self):
        return self.publisher_is_draft == self.STATE_PUBLISHED

    def get_draft(self):
        """
        Returns draft version of any instance (draft or public)
        :return:
        """
        if self.is_draft:
            return self
        return self.publisher_draft

    def get_published(self):
        """
        Returns published version of any instance (draft or public)
        :return:
        """
        if self.is_public:
            return self
        return self.publisher_linked


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
            draft_obj = self
            if draft_obj.publisher_linked:
                draft_obj.publisher_linked.delete()

            publish_obj = self.__class__.objects.get(pk=self.pk)
            publish_obj.pk = None
            publish_obj.id = None
            publish_obj.created = None
            publish_obj.modified = None
            publish_obj.publisher_is_draft = self.STATE_PUBLISHED
            publish_obj.save()
            self.copy_relations(draft_obj, publish_obj)
            draft_obj.publisher_linked = publish_obj
            draft_obj.save()

    def copy_relations(self, src, dst):
        pass

    def delete(self, **kwargs):
        if self.publisher_is_draft:
            if self.publisher_linked:
                self.publisher_linked.delete()
        return super(PublisherModel, self).delete(**kwargs)


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


class ArrayLength(models.Func):
    """
    Annotate array fields with their length
    usage: MyModel.objects.all().annotate(field_len=ArrayLength('field')).order_by('field_len')
    """
    function = 'CARDINALITY'
