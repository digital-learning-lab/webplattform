import csv

from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponse

from dll.communication.models import CommunicationEvent, CommunicationEventType, NewsletterSubscrption

admin.site.register(CommunicationEvent)
admin.site.register(CommunicationEventType)


@admin.register(NewsletterSubscrption)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'doi_confirmed')
    change_list_template = "admin/newsletter_subscription_changelist.html"

    def get_urls(self):
        urls = super(NewsletterSubscriptionAdmin, self).get_urls()
        custom_urls = [
            url(r'export-subscriptions/', self.export_subscriptions)
        ]
        return custom_urls + urls

    def export_subscriptions(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="newsletter_subscriptions.csv"'
        writer = csv.writer(response)
        writer.writerow(['id', 'email', 'confirmation_date'])
        for sub in self.get_queryset(request).filter(doi_confirmed=True):
            if sub.doi_confirmed_date:
                date = sub.doi_confirmed_date.strftime("%d-%m-%Y")
            else:
                # just in case the subscription was added manually in the admin
                date = ''
            writer.writerow([sub.pk, sub.email, date])
        return response
