from rest_framework.serializers import ModelSerializer

from dll.survey.models import Trigger


class TriggerSerializer(ModelSerializer):
    class Meta:
        model = Trigger
        fields = ["id", "event", "delay", "survey", "url", "target"]
