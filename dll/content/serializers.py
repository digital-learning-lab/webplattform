import logging

from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from easy_thumbnails.files import get_thumbnailer
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from dll.communication.models import CoAuthorshipInvitation
from dll.communication.tokens import co_author_invitation_token
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


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['status', 'json_data']


class BaseContentSubclassSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True, allow_null=True, required=False)
    contentlink_set = LinkSerializer(many=True, required=False)
    review = ReviewSerializer(read_only=True)

    def validate_related_content(self, data):
        return (x.is_public for x in data)

    def create(self, validated_data):
        links_data = validated_data.pop('contentlink_set')
        co_authors = validated_data.pop('co_authors')
        content = super(BaseContentSubclassSerializer, self).create(validated_data)
        self._update_content_links(content, links_data)
        self._update_co_authors(content, co_authors)
        return content

    def update(self, instance, validated_data):
        """
        `update_methods` provides a mapping of keys present in the serialized data that need further processing, and
        maps it to the corresponding processing method
        """
        update_methods = {
            'contentlink_set': '_update_content_links',
            'co_authors': '_update_co_authors'
        }
        for update_key, update_method in update_methods.items():
            try:
                data = validated_data.pop(update_key)
                method = getattr(self, update_method)
            except AttributeError:
                logger.warning("No update method for {}".format(update_key))
                pass
            except KeyError:
                # this key was not present in the serialized data, so it doesn't have to be updated
                pass
            else:
                method(instance, data)
        instance = super().update(instance, validated_data)
        return instance

    def _update_content_links(self, content, data):
        """
        delete all previous links first, because we can't distinguish whether it is a new link, or an old one with
        updated href AND name AND ...
        """
        content.contentlink_set.all().delete()
        for link in data:
            ContentLink.objects.create(content=content, **dict(link))

    def _update_co_authors(self, content, co_authors):
        current_co_authors = set(content.co_authors.all())
        updated_list = set(co_authors)
        new_co_authors = updated_list - current_co_authors
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


# todo: file serializer
