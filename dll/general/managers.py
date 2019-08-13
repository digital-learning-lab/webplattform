from django.db.models import QuerySet


class PublisherQuerySetMixin:
    def drafts(self):
        from .models import PublisherModelBase
        return self.filter(publisher_is_draft=PublisherModelBase.STATE_DRAFT)

    def published(self):
        from .models import PublisherModelBase
        return self.filter(publisher_is_draft=PublisherModelBase.STATE_PUBLISHED)


class PublisherQuerySet(PublisherQuerySetMixin, QuerySet):
    pass
