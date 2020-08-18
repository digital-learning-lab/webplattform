# -*- coding: utf-8 -*-
import csv

from dll.content.models import Favorite
from dll.communication.models import NewsletterSubscrption


def create_newsletter_subscriptions_from_csv(csvfile):
    reader = csv.reader(csvfile)
    for row in reader:
        NewsletterSubscrption.objects.update_or_create(email=row[0], doi_confirmed=True)


def is_favored(user, content):
    favored = False
    if user.is_authenticated:
        favored = Favorite.objects.filter(
            user=user, content=content.get_draft()
        ).exists()
    return favored
