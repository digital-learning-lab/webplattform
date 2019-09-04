from django.db.models import signals
from django.dispatch import Signal


post_publish = Signal(providing_args=['instance'])
post_unpublish = Signal(providing_args=['instance'])


def unpublish(sender, instance, using, **kwargs):
    if getattr(instance, 'publisher_is_draft', None) is False:
        post_unpublish.send(sender=sender, instance=instance)


signals.post_delete.connect(unpublish)
