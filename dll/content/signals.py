from haystack.signals import BaseSignalProcessor

from dll.content.models import TeachingModule, Tool, Trend
from dll.general.signals import post_publish, post_unpublish


class ContentSignalProcessor(BaseSignalProcessor):
    def setup(self):
        post_publish.connect(self.handle_save, sender=TeachingModule)
        post_publish.connect(self.handle_save, sender=Tool)
        post_publish.connect(self.handle_save, sender=Trend)
        post_unpublish.connect(self.handle_delete, sender=TeachingModule)
        post_unpublish.connect(self.handle_delete, sender=Tool)
        post_unpublish.connect(self.handle_delete, sender=Trend)

    def teardown(self):
        post_publish.disconnect(self.handle_save, sender=TeachingModule)
        post_publish.disconnect(self.handle_save, sender=Tool)
        post_publish.disconnect(self.handle_save, sender=Trend)
        post_unpublish.disconnect(self.handle_delete, sender=TeachingModule)
        post_unpublish.disconnect(self.handle_delete, sender=Tool)
        post_unpublish.disconnect(self.handle_delete, sender=Trend)
