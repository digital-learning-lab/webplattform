import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from psycopg2._range import NumericRange
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, IntegerField, CharField
from rest_framework.relations import RelatedField
from rest_polymorphic.serializers import PolymorphicSerializer

from dll.communication.models import CoAuthorshipInvitation
from dll.content.fields import RangeField
from dll.content.models import SchoolType, Competence, SubCompetence, Subject, OperatingSystem, ToolApplication, \
    HelpText, Content, Tool, Trend, TeachingModule, ContentLink, Review, ToolLink
from dll.general.utils import custom_slugify
from dll.user.models import DllUser


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
        return obj.get_image()

    def get_co_authors(self, obj):
        return [f'{author.full_name}' for author in obj.co_authors.all()]

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
        return str(obj.author.full_name)

    def get_preview_url(self, obj):
        return obj.get_preview_url()

    def get_edit_url(self, obj):
        return obj.get_edit_url()

    def get_status(self, obj):
        status = _('Draft')
        if obj.publisher_linked:
            if obj.review:
                if obj.review.status == Review.DECLINED:
                    return _('Approved - Resubmission declined.')
                else:
                    return _('Approved - Resubmission pending.')
            return _('Approved')

        if obj.publisher_is_draft and obj.review and obj.review.status == Review.DECLINED:
            return _('Declined')

        if obj.publisher_is_draft and obj.reviews.count():
            return _('Submitted')

        return status

    class Meta(ContentListSerializer.Meta):
        fields = ['id', 'name', 'image', 'type', 'type_verbose', 'teaser', 'competences', 'url', 'created',
                  'co_authors', 'preview_url', 'edit_url', 'author', 'status']


class ContentListInvitationSerializer(ContentListInternalSerializer):
    invitation_url = serializers.SerializerMethodField()

    def get_invitation_url(self, obj):
        return reverse('communication:coauthor-invitation-internal', kwargs={'pk': obj.pk})

    class Meta(ContentListSerializer.Meta):
        fields = ['id', 'name', 'image', 'type', 'type_verbose', 'teaser', 'competences', 'url', 'created',
                  'co_authors', 'preview_url', 'edit_url', 'author', 'status', 'invitation_url']


class ContentListInternalReviewSerializer(ContentListInternalSerializer):
    review_url = SerializerMethodField(allow_null=True)
    assign_reviewer_url = SerializerMethodField(allow_null=True)
    unassign_reviewer_url = SerializerMethodField(allow_null=True)

    has_assigned_reviewer = serializers.SerializerMethodField(allow_null=True)
    reviewer = serializers.SerializerMethodField(allow_null=True)
    can_unassign = serializers.SerializerMethodField(allow_null=False)
    can_assign = serializers.SerializerMethodField(allow_null=False)
    can_claim = serializers.SerializerMethodField(allow_null=False)

    def get_review_url(self, obj):
        return obj.get_review_url()

    def get_has_assigned_reviewer(self, obj):
        return obj.has_assigned_reviewer

    def get_assign_reviewer_url(self, obj):
        return obj.get_assign_reviewer_url()

    def get_unassign_reviewer_url(self, obj):
        return obj.get_unassign_reviewer_url()

    def get_can_unassign(self, obj):
        user = self.context.get('request').user
        return user and obj.review and obj.review.assigned_reviewer and obj.review.assigned_reviewer == user

    def get_can_assign(self, obj):
        """Provides information whether current user can assign others as reviewers."""
        user = self.context.get('request').user
        return user.has_perm('content.assign_reviewer')

    def get_can_claim(self, obj):
        """Provides information whether current user can assign others as reviewers."""
        user = self.context.get('request').user
        return user.has_perm('content.claim_review', obj.review)

    def get_reviewer(self, obj):
        if obj.review and obj.review.assigned_reviewer:
            return obj.review.assigned_reviewer.full_name
        return None

    class Meta(ContentListInternalSerializer.Meta):
        fields = ['id', 'name', 'image', 'type', 'type_verbose', 'teaser', 'competences', 'url', 'created', 'reviewer',
                  'co_authors', 'preview_url', 'edit_url', 'author', 'status', 'review_url', 'has_assigned_reviewer',
                  'assign_reviewer_url', 'can_unassign', 'unassign_reviewer_url', 'can_assign', 'can_claim']


class AuthorSerializer(serializers.ModelSerializer):
    username = SerializerMethodField(allow_null=True)

    def get_username(self, obj):
        return obj.full_name

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


class RelatedContentField(DllM2MField):

    def to_representation(self, value):
        try:
            content = Content.objects.get(pk=value.pk).get_published()
            if content:
                pk = content.pk
                label = content.name
            else:
                return {}
        except Content.DoesNotExist:
            return {}
        return {'pk': pk, 'label': label}

    def to_internal_value(self, data):
        pk = data['pk']
        content = Content.objects.get(pk=pk)
        return content.get_draft().pk


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['status', 'json_data']


class AdditionalToolsField(RelatedField):
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return str(value)


class BaseContentSubclassSerializer(serializers.ModelSerializer):
    name = CharField(required=True)
    image = SerializerMethodField()
    author = AuthorSerializer(read_only=True, allow_null=True, required=False)
    contentlink_set = LinkSerializer(many=True, allow_null=True, required=False)
    co_authors = DllM2MField(allow_null=True, many=True, required=False, queryset=DllUser.objects.all())
    competences = DllM2MField(allow_null=True, many=True, queryset=Competence.objects.all())
    sub_competences = DllM2MField(allow_null=True, many=True, queryset=SubCompetence.objects.all())
    related_content = RelatedContentField(allow_null=True, many=True, queryset=Content.objects.drafts())
    tools = SerializerMethodField(allow_null=True)
    trends = SerializerMethodField(allow_null=True)
    teaching_modules = SerializerMethodField(allow_null=True)
    review = ReviewSerializer(read_only=True)
    help_texts = SerializerMethodField(allow_null=True)
    preview_url = SerializerMethodField(allow_null=True)
    submitted = SerializerMethodField(allow_null=True)
    pending_co_authors = SerializerMethodField(allow_null=True)
    content_files = SerializerMethodField(allow_null=True)
    additional_tools = AdditionalToolsField(many=True, allow_null=True, required=False, queryset=Tool.objects.drafts(),
                                            source='get_additional_tools', write_only=True)

    def validate_name(self, data):
        """Make sure the slug of this name will be unique too."""
        expected_slug = custom_slugify(data)
        if (self.instance is None and Content.objects.drafts().filter(slug=expected_slug).count() >= 1) or \
                Content.objects.published().filter(slug=expected_slug).count() > 1:
            raise ValidationError(_('A content with this name already exists.'))
        return data

    def validate_related_content(self, data):
        res = []
        for x in data:
            obj = Content.objects.get(pk=x)
            if obj.is_draft:
                res.append(x)
        return res

    def get_content_files(self, obj):
        return [{'title': file.title, 'url': file.file.url, 'id': file.id} for file in obj.content_files.all()]

    def get_pending_co_authors(self, obj):
        return [invite.to.full_name for invite in obj.invitations.filter(accepted__isnull=True)]

    def get_submitted(self, obj):
        return obj.review and (obj.review.status == Review.IN_PROGRESS or obj.review.status == Review.NEW)

    def get_help_texts(self, obj):
        result = {}
        try:
            help_text = HelpText.objects.get(content_type=ContentType.objects.get_for_model(obj))
            for field in help_text.help_text_fields.all():
                result[field.name.split('.')[-1].strip('>')] = field.text
        except HelpText.DoesNotExist:
            pass
        return result

    def get_preview_url(self, obj):
        return obj.get_preview_url()

    def get_image(self, obj):
        if obj.image:
            return {'name': str(obj.image), 'url': obj.image.url}
        return None

    def _get_content_name(self, content):
        pub = content.get_published()
        if pub:
            return pub.name
        return content.name

    def get_tools(self, obj):
        return [{'pk': content.pk, 'label': self._get_content_name(content)}
                for content in obj.related_content.drafts().instance_of(Tool)]

    def get_trends(self, obj):
        return [{'pk': content.pk, 'label': self._get_content_name(content)}
                for content in obj.related_content.drafts().instance_of(Trend)]

    def get_teaching_modules(self, obj):
        return [{'pk': content.pk, 'label': self._get_content_name(content)}
                for content in obj.related_content.drafts().instance_of(TeachingModule)]

    def get_m2m_fields(self):
        return [
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
        co_authors = validated_data.pop('co_authors', [])
        additional_tools = validated_data.pop('get_additional_tools', [])
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

    def _update_co_authors(self, content, co_authors):
        invited_co_authors = set(DllUser.objects.filter(pk__in=content.invitations.filter(accepted__isnull=True)
                                                        .values_list('to', flat=True)))
        current_co_authors = set(content.co_authors.all())
        updated_list = set(DllUser.objects.filter(pk__in=co_authors))
        new_co_authors = updated_list - current_co_authors - invited_co_authors
        removed_co_authors = current_co_authors - updated_list
        content.co_authors.remove(*removed_co_authors)
        for user in new_co_authors:
            invitation = CoAuthorshipInvitation.objects.create(
                by=self.context['request'].user,
                to=user,
                content=content,
                site_id=settings.SITE_ID
            )
            invitation.send_invitation_mail()

    def _update_m2m_fields(self, instance, field, values):
        for pk in values:
            getattr(instance, field).add(pk)
        for pk in getattr(instance, field).values_list('pk', flat=True):
            if pk not in values:
                getattr(instance, field).remove(pk)

    def _update_array_fields(self, instance, field, values):
        setattr(instance, field, values)

    def update(self, instance, validated_data):
        """
        `update_methods` provides a mapping of keys present in the serialized data that need further
        processing, and
        maps it to the corresponding processing method
        """
        update_methods = {
            'contentlink_set': '_update_content_links',
            'co_authors': '_update_co_authors'
        }
        for update_key, update_method in update_methods.items():
            try:
                data = validated_data.pop(update_key, [])
                method = getattr(self, update_method)
            except AttributeError:
                logger.warning("No update method for {}".format(update_key))
                pass
            except KeyError:
                # this key was not present in the serialized data, so it doesn't have to be updated
                pass
            else:
                method(instance, data)

        for field in self.get_m2m_fields():
            try:
                values = validated_data.pop(field)
            except KeyError:
                pass
            else:
                self._update_m2m_fields(instance, field, values)

        for field in self.get_array_fields():
            try:
                values = validated_data.pop(field)
            except KeyError:
                pass
            else:
                self._update_array_fields(instance, field, values)

        additional_tools = validated_data.pop('get_additional_tools', [])
        for tool in additional_tools:
            if tool.get('name') and tool.get('url'):
                tool_instance = Tool.objects.create(
                name=tool['name'],
                author=instance.author
                )
                tool_instance.related_content.add(instance)
                tool_instance.save()
                ToolLink.objects.create(tool=tool_instance, url=tool['url'])
            else:
                raise ValidationError({'additional_tools': [_('All additional tools must contain a name and an URL.')]})
        instance = super().update(instance, validated_data)
        return instance


class ToolLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = ToolLink
        fields = ['url', 'name']


class ToolSerializer(BaseContentSubclassSerializer):
    operating_systems = DllM2MField(allow_null=True, many=True, queryset=OperatingSystem.objects.all(), required=False)
    applications = DllM2MField(allow_null=True, many=True, queryset=ToolApplication.objects.all(), required=False)
    url = ToolLinkSerializer(allow_null=True, many=False, required=False)

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
        if instance:
            try:
                if instance.url:
                    instance.url.delete()
            except ObjectDoesNotExist:
                pass
            url = validated_data.pop('url', None)
            if url:
                ToolLink.objects.create(**url, tool=instance)

        instance = super(ToolSerializer, self).update(instance, validated_data)
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

    class Meta:
        model = Trend
        fields = '__all__'


class TeachingModuleSerializer(BaseContentSubclassSerializer):
    subjects = DllM2MField(allow_null=True, many=True, queryset=Subject.objects.all())
    school_types = DllM2MField(allow_null=True, many=True, queryset=SchoolType.objects.all())
    school_class = RangeField(NumericRange, child=IntegerField(allow_null=True), required=False, allow_null=True)

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


class ContentPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Tool: ToolSerializer,
        Trend: TrendSerializer,
        TeachingModule: TeachingModuleSerializer
    }


class ImageFileSerializer(serializers.Serializer):
    image = serializers.FileField()


class FileSerializer(serializers.Serializer):
    file = serializers.FileField()
