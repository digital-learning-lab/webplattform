import logging

from django.utils.translation import ugettext_lazy as _

from easy_thumbnails.files import get_thumbnailer
from psycopg2._range import NumericRange
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, IntegerField, CharField
from rest_framework.relations import RelatedField
from rest_framework.validators import UniqueValidator
from rest_polymorphic.serializers import PolymorphicSerializer

from dll.communication.models import CoAuthorshipInvitation
from dll.content.fields import RangeField
from dll.content.models import SchoolType, Competence, SubCompetence, Subject, OperatingSystem, ToolApplication
from dll.user.models import DllUser
from .models import Content, Tool, Trend, TeachingModule, ContentLink, Review


logger = logging.getLogger('dll.communication.serializers')


class ContentListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()  # WARNING: can conflict with Content.image
    type = serializers.SerializerMethodField()
    type_verbose = serializers.SerializerMethodField()
    competences = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    created = serializers.DateTimeField(format="%d.%m.%Y")
    co_authors = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = ['id', 'name', 'image', 'type', 'type_verbose', 'teaser', 'competences', 'url', 'created',
                  'co_authors']

    def get_image(self, obj):
        if obj.image is not None:
            thumbnailer = get_thumbnailer(obj.image)
            thumb = thumbnailer.get_thumbnail({'size': (300,300)})
            return str(thumb)
        else:
            return None

    def get_co_authors(self, obj):
        return [f'{author.username}' for author in obj.co_authors.all()]

    def get_type(self, obj):
        return obj.type

    def get_type_verbose(self, obj):
        return obj.type_verbose

    def get_competences(self, obj):
        competences = obj.competences.all()
        return [i.icon_class for i in competences]

    def get_url(self, obj):
        return obj.get_absolute_url()


class ContentListInternalSerializer(ContentListSerializer):
    author = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    edit_url = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_author(self, obj):
        return str(obj.author.username)

    def get_preview_url(self, obj):
        return obj.get_absolute_url()

    def get_edit_url(self, obj):
        return obj.get_edit_url()

    def get_status(self, obj):
        status = _('Draft')
        if not obj.publisher_is_draft:
            status = _('Approved')

        if obj.publisher_is_draft and obj.reviews.all().count():
            status = _('Submitted')

        return status


    class Meta(ContentListSerializer.Meta):
        fields = ['id', 'name', 'image', 'type', 'type_verbose', 'teaser', 'competences', 'url', 'created',
                  'co_authors', 'preview_url', 'edit_url', 'author', 'status']


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


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['status', 'json_data']


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

    review = ReviewSerializer(read_only=True)

    def validate_related_content(self, data):
        res = []
        for x in data:
            obj = Content.objects.get(pk=x)
            if obj.is_public:
                res.append(x)
        return res

    def get_image(self, obj):
        if obj.image:
            return {'name': str(obj.image), 'url': obj.image.url}
        return None

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
        self._update_content_links(content, links_data)
        self._update_co_authors(content, co_authors)
        return content

    def _update_content_links(self, content, data):
        """
        delete all previous links first, because we can't distinguish whether it is a new link, or an old one with
        updated href AND name AND ...
        """
        content.contentlink_set.all().delete()
        for link in data:
            ContentLink.objects.create(content=content, **dict(link))

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

        co_authors = validated_data['co_authors']
        self._update_co_authors(instance, co_authors)

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

    def _update_co_authors(self, content, co_authors):
        current_co_authors = set(content.co_authors.all())
        updated_list = set(co_authors)
        new_co_authors = updated_list - current_co_authors
        removed_co_authors = current_co_authors - updated_list
        content.co_authors.remove(*removed_co_authors)
        for user in new_co_authors:
            CoAuthorshipInvitation.objects.create(
                by=self.context['request'].user,
                to=user,
                content=content
            )


class ToolSerializer(BaseContentSubclassSerializer):
    operating_systems = DllM2MField(allow_null=True, many=True, queryset=OperatingSystem.objects.all(), required=False)
    applications = DllM2MField(allow_null=True, many=True, queryset=ToolApplication.objects.all(), required=False)

    def get_array_fields(self):
        fields = super(ToolSerializer, self).get_array_fields()
        fields.extend([
            'pro',
            'contra'
        ])
        return fields

    def get_m2m_fields(self):
        fields = super(ToolSerializer, self).get_m2m_fields()
        fields.extend([
            'operating_systems',
            'applications'
        ])
        return fields

    def update(self, instance, validated_data):
        instance = super(ToolSerializer, self).update(instance, validated_data)

        instance.status = validated_data.get('status', None)
        instance.requires_registration = validated_data.get('requires_registration', None)
        instance.usk = validated_data.get('usk', None)
        instance.privacy = validated_data.get('privacy', None)
        instance.description = validated_data.get('description', None)
        instance.usage = validated_data.get('usage', None)

        instance.save()
        return instance

    class Meta:
        model = Tool
        fields = '__all__'


class TrendSerializer(BaseContentSubclassSerializer):

    def get_array_fields(self):
        fields = super(TrendSerializer, self).get_array_fields()
        fields.extend([
            'target_group',
            'publisher'
        ])
        return fields

    def update(self, instance, validated_data):
        instance = super(TrendSerializer, self).update(instance, validated_data)

        instance.language = validated_data.get('language', None)
        instance.licence = validated_data.get('licence', None)
        instance.category = validated_data.get('category', None)
        instance.publisher_date = validated_data.get('publisher_date', None)
        instance.central_contents = validated_data.get('central_contents', None)
        instance.citation_info = validated_data.get('citation_info', None)

        instance.save()

        return instance

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


# todo: file serializer


class FileSerializer(serializers.Serializer):
    image = serializers.FileField()
