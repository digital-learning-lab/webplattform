from django.contrib import admin

from dll.communication.models import CommunicationEvent, CommunicationEventType

admin.site.register(CommunicationEvent)
admin.site.register(CommunicationEventType)
