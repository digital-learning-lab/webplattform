from django.db import models
from django.dispatch import receiver
from haystack.signals import BaseSignalProcessor

from dll.content.models import TeachingModule, Tool, Trend, Content, ContentFile
from dll.general.signals import post_publish, post_unpublish
import sys

TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"


class ContentSignalProcessor(BaseSignalProcessor):
    def setup(self):
        if not TESTING:
            post_publish.connect(self.handle_save, sender=TeachingModule)
            post_publish.connect(self.handle_save, sender=Tool)
            post_publish.connect(self.handle_save, sender=Trend)
            post_unpublish.connect(self.handle_delete, sender=TeachingModule)
            post_unpublish.connect(self.handle_delete, sender=Tool)
            post_unpublish.connect(self.handle_delete, sender=Trend)

    def teardown(self):
        if not TESTING:
            post_publish.disconnect(self.handle_save, sender=TeachingModule)
            post_publish.disconnect(self.handle_save, sender=Tool)
            post_publish.disconnect(self.handle_save, sender=Trend)
            post_unpublish.disconnect(self.handle_delete, sender=TeachingModule)
            post_unpublish.disconnect(self.handle_delete, sender=Tool)
            post_unpublish.disconnect(self.handle_delete, sender=Trend)


@receiver(models.signals.post_delete, sender=Content)
def auto_delete_filer_image_on_delete(sender, instance, **kwargs):
    # for reasons unknown, this works without specifying the concrete sender model
    if instance.image:
        instance.image.delete()


@receiver(models.signals.post_delete, sender=ContentFile)
def auto_delete_filer_file_on_delete(sender, instance, **kwargs):
    instance.file.delete()
