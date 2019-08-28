from haystack import indexes

from dll.content.models import Content


class ContentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name', boost=2)
    teaser = indexes.CharField(model_attr='teaser', boost=1.5)
    additional_info = indexes.CharField(model_attr='additional_info', boost=1)
    tags = indexes.MultiValueField()
    published = indexes.DateTimeField(model_attr='created')

    def get_model(self):
        return Content

    def index_queryset(self, using=None):
        return self.get_model().objects.published()

    def prepare_tags(self, obj):
        return list(obj.tags.values_list('name', flat=True))
