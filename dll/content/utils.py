# -*- coding: utf-8 -*-
import csv

from dll.communication.models import NewsletterSubscrption


def create_newsletter_subscriptions_from_csv(csvfile):
    reader = csv.reader(csvfile)
    for row in reader:
        NewsletterSubscrption.objects.update_or_create(email=row[0], doi_confirmed=True)
