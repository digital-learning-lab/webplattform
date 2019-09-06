from haystack import indexes

from dll.content.models import Content, Tool, TeachingModule, Trend


class ContentIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name', boost=2)
    teaser = indexes.CharField(model_attr='teaser', boost=1.5, null=True)
    additional_info = indexes.CharField(model_attr='additional_info', boost=1, null=True)
    tags = indexes.MultiValueField()
    authors = indexes.MultiValueField()
    published = indexes.DateTimeField(model_attr='created')

    def get_model(self):
        return Content

    def index_queryset(self, using=None):
        return self.get_model().objects.published()

    def prepare_name(self, obj):
        return obj.name

    def prepare_tags(self, obj):
        return list(obj.tags.values_list('name', flat=True))

    def prepare_authors(self, obj):
        """
        a list of author and all co-authors full names
        """
        return [obj.author.full_name, *[i.full_name for i in obj.co_authors.all()]]


class ToolsIndex(ContentIndex, indexes.Indexable):
    operating_systems = indexes.MultiValueField()

    def get_model(self):
        return Tool

    def prepare_operating_systems(self, obj):
        return list(obj.operating_systems.values_list('name', flat=True))


class TeachingModulesIndex(ContentIndex, indexes.Indexable):
    subjects = indexes.MultiValueField()

    def get_model(self):
        return TeachingModule

    def prepare_subjects(self, obj):
        return list(obj.subjects.values_list('name', flat=True))


class TrendsIndex(ContentIndex, indexes.Indexable):

    def get_model(self):
        return Trend
