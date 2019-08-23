from django.utils.translation import ugettext_lazy as _

from easy_thumbnails.files import get_thumbnailer
from psycopg2._range import NumericRange
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, IntegerField, CharField
from rest_framework.relations import RelatedField
from rest_framework.validators import UniqueValidator
from rest_polymorphic.serializers import PolymorphicSerializer

from dll.content.fields import RangeField
from dll.content.models import SchoolType, Competence, SubCompetence, Subject
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
        fields = ['username', 'pk']


class SchoolTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolType
        fields = ['name', 'pk']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['name', 'pk']


class CompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competence
        fields = ['name', 'pk']


class SubCompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCompetence
        fields = ['name', 'pk']


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentLink
        fields = ['url', 'name', 'type']
        depth = 1


class DllM2MField(RelatedField):

    def to_representation(self, value):
        try:
            label = getattr(value, 'username')
        except AttributeError:
            label = getattr(value, 'name')
        return {'pk': value.pk, 'label': label}

    def to_internal_value(self, data):
        return data['pk']


class BaseContentSubclassSerializer(serializers.ModelSerializer):
    name = CharField(required=True, validators=[
        UniqueValidator(
            queryset=Content.objects.all(),
            message=_('A content with this name already exists.')
        )
    ])
    image = SerializerMethodField()
    author = AuthorSerializer(read_only=True, allow_null=True, required=False)
    contentlink_set = LinkSerializer(many=True, allow_null=True, required=False)
    co_authors = DllM2MField(allow_null=True, many=True, queryset=DllUser.objects.all())
    competences = DllM2MField(allow_null=True, many=True, queryset=Competence.objects.all())
    sub_competences = DllM2MField(allow_null=True, many=True, queryset=SubCompetence.objects.all())
    related_content = DllM2MField(allow_null=True, many=True, queryset=Content.objects.all())
    tools = SerializerMethodField(allow_null=True)
    trends = SerializerMethodField(allow_null=True)
    teaching_modules = SerializerMethodField(allow_null=True)

    def validate_related_content(self, data):
        res = []
        for x in data:
            obj = Content.objects.get(pk=x)
            if obj.is_public:
                res.append(x)
        return res

    def get_image(self, obj):
        return {'name': str(obj.image), 'url': obj.image.url}

    def get_tools(self, obj):
        return [{'pk': content.pk, 'label': content.name} for content in obj.related_content.instance_of(Tool)]

    def get_trends(self, obj):
        return [{'pk': content.pk, 'label': content.name} for content in obj.related_content.instance_of(Trend)]

    def get_teaching_modules(self, obj):
        return [{'pk': content.pk, 'label': content.name} for content in obj.related_content.instance_of(TeachingModule)]

    def get_m2m_fields(self):
        return [
            'co_authors',
            'competences',
            'sub_competences',
            'related_content'
        ]

    def get_array_fields(self):
        return [
            'learning_goals',
        ]

    def create(self, validated_data):
        links_data = validated_data.pop('contentlink_set', [])
        content = super(BaseContentSubclassSerializer, self).create(validated_data)
        for link in links_data:
            ContentLink.objects.create(content=content, **dict(link))
        return content

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.teaser = validated_data['teaser']
        instance.additional_info = validated_data['additional_info']

        links_data = validated_data.pop('contentlink_set', [])
        if links_data:
            instance.contentlink_set.all().delete()
            for link in links_data:
                if not instance.contentlink_set.filter(url=link['url'], name=link['name'], type=link['type']).exists():
                    ContentLink.objects.create(content=instance, **dict(link))


        for field in self.get_m2m_fields():
            values = validated_data.pop(field)
            for pk in values:
                getattr(instance, field).add(pk)
            for pk in getattr(instance, field).values_list('pk', flat=True):
                if pk not in values:
                    getattr(instance, field).remove(pk)

        for field in self.get_array_fields():
            values = validated_data.pop(field)
            if values:
                setattr(instance, field, values)
            else:
                setattr(instance, field, [])
        instance.save()
        return instance


class ToolSerializer(BaseContentSubclassSerializer):
    class Meta:
        model = Tool
        fields = '__all__'


class TrendSerializer(BaseContentSubclassSerializer):
    class Meta:
        model = Trend
        fields = '__all__'


class TeachingModuleSerializer(BaseContentSubclassSerializer):
    subjects = DllM2MField(allow_null=True, many=True, queryset=Subject.objects.all())
    school_types = DllM2MField(allow_null=True, many=True, queryset=Subject.objects.all())
    school_class = RangeField(NumericRange, child=IntegerField(), required=False, allow_null=True)

    def get_array_fields(self):
        fields = super(TeachingModuleSerializer, self).get_array_fields()
        fields.extend([
            'expertise',
            'equipment',
            'estimated_time',
            'subject_of_tuition',
        ])
        return fields
    
    class Meta:
        model = TeachingModule
        fields = '__all__'

    def get_m2m_fields(self):
        fields = super(TeachingModuleSerializer, self).get_m2m_fields()
        fields.extend([
            'subjects',
            'school_types',
        ])
        return fields

    def update(self, instance, validated_data):
        instance = super(TeachingModuleSerializer, self).update(instance, validated_data)

        instance.description = validated_data.get('description', None)
        instance.educational_plan_reference = validated_data.get('educational_plan_reference', None)
        instance.state = validated_data.get('state', None)
        instance.differentiating_attribute = validated_data.get('differentiating_attribute', None)
        instance.licence = validated_data.get('licence', None)
        instance.school_class = validated_data.get('school_class', None)

        instance.save()

        return instance


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


class FileSerializer(serializers.Serializer):
    image = serializers.FileField()
