from polymorphic.query import PolymorphicQuerySet

from dll.general.managers import PublisherQuerySetMixin


class ContentQuerySet(PublisherQuerySetMixin, PolymorphicQuerySet):

    def tools(self):
        from .models import Content
        return self.none()

    def teaching_modules(self):
        from .models import Content
        return self.none()

    def trends(self):
        from .models import Content
        return self.none()
