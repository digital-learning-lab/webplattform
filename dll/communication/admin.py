from django.contrib import admin

from dll.communication.models import CommunicationEvent, CommunicationEventType, NewsletterSubscrption

admin.site.register(CommunicationEvent)
admin.site.register(CommunicationEventType)


@admin.register(NewsletterSubscrption)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'doi_confirmed')
