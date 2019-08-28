from haystack import indexes

from dll.content.models import Content


class ContentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    published = indexes.DateTimeField(model_attr='created')

    def get_model(self):
        return Content

    def index_queryset(self, using=None):
        return self.get_model().objects.published()
