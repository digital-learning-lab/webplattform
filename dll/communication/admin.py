import csv

from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path

from dll.communication.forms import CsvImportForm
from dll.communication.models import CommunicationEvent, CommunicationEventType, NewsletterSubscrption
from dll.content.utils import create_newsletter_subscriptions_from_csv

admin.site.register(CommunicationEvent)
admin.site.register(CommunicationEventType)


@admin.register(NewsletterSubscrption)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'doi_confirmed')
    change_list_template = "admin/newsletter_subscription_changelist.html"

    def get_urls(self):
        urls = super(NewsletterSubscriptionAdmin, self).get_urls()
        custom_urls = [
            path('export-subscriptions/', self.export_subscriptions),
            path('import-subscriptions/', self.import_csv),
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

    def import_csv(self, request):
        print('here')
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            with open('/tmp/subs.csv', 'wb+') as destination:
                for chunk in csv_file.chunks():
                    destination.write(chunk)
            with open('/tmp/subs.csv') as csv_file:
                create_newsletter_subscriptions_from_csv(csv_file)
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/csv_form.html", payload
        )
