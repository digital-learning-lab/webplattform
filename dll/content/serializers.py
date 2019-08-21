from easy_thumbnails.files import get_thumbnailer
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from dll.user.models import DllUser
from .models import Content, Tool, Trend, TeachingModule, ContentLink, Review


class ContentListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()  # WARNING: can conflict with Content.image
    type = serializers.SerializerMethodField()
    type_verbose = serializers.SerializerMethodField()
    competences = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    created = serializers.DateTimeField(format="%d.%m.%Y")

    class Meta:
        model = Content
        fields = ['id', 'name', 'image', 'type', 'type_verbose', 'teaser', 'competences', 'url', 'created']

    def get_image(self, obj):
        if obj.image is not None:
            thumbnailer = get_thumbnailer(obj.image)
            thumb = thumbnailer.get_thumbnail({'size': (300,300)})
            return str(thumb)
        else:
            return None

    def get_type(self, obj):
        return obj.type

    def get_type_verbose(self, obj):
        return obj.type_verbose

    def get_competences(self, obj):
        competences = obj.competences.all()
        return [i.icon_class for i in competences]

    def get_url(self, obj):
        return obj.get_absolute_url()


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DllUser
        fields = ['username']


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentLink
        fields = ['url', 'name', 'type']
        depth = 1


class BaseContentSubclassSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True, allow_null=True, required=False)
    contentlink_set = LinkSerializer(many=True)

    def validate_related_content(self, data):
        return (x.is_public for x in data)

    def create(self, validated_data):
        links_data = validated_data.pop('contentlink_set')
        content = super(BaseContentSubclassSerializer, self).create(validated_data)
        for link in links_data:
            ContentLink.objects.create(content=content, **dict(link))
        return content

    # TODO: update


class ToolSerializer(BaseContentSubclassSerializer):
    class Meta:
        model = Tool
        fields = '__all__'


class TrendSerializer(BaseContentSubclassSerializer):
    class Meta:
        model = Trend
        fields = '__all__'


class TeachingModuleSerializer(BaseContentSubclassSerializer):
    class Meta:
        model = TeachingModule
        fields = '__all__'


class ContentPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Tool: ToolSerializer,
        Trend: TrendSerializer,
        TeachingModule: TeachingModuleSerializer
    }


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['status', 'json_data']
