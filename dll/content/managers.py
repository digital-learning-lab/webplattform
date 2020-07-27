from django.db.models import Count
from polymorphic.query import PolymorphicQuerySet

from dll.general.managers import PublisherQuerySetMixin


class ContentQuerySet(PublisherQuerySetMixin, PolymorphicQuerySet):
    def tools(self):
        from .models import Tool

        return self.instance_of(Tool)

    def teaching_modules(self):
        from .models import TeachingModule

        return self.instance_of(TeachingModule)

    def trends(self):
        from .models import Trend

        return self.instance_of(Trend)

    def order_by_number_of_coauthors(self, desc=True):
        return self.annotate(n=Count("co_authors")).order_by("-n" if desc else "n")
