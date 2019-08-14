from rest_framework import serializers

from .models import Content


class ContentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Content
        fields = ['name']
