# -*- coding: utf-8 -*-
import csv
import random

from dll.content.models import Favorite, Content, Tool, Trend, TeachingModule
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


def get_random_content(limit_teaching_modules, limit_tools, limit_trends):
    content_pks = []
    try:
        content_pks += random.choices(
            TeachingModule.objects.published().values_list("pk", flat=True),
            k=limit_teaching_modules,
        )
        content_pks += random.choices(
            Trend.objects.published().values_list("pk", flat=True), k=limit_tools
        )
        content_pks += random.choices(
            Tool.objects.published().values_list("pk", flat=True), k=limit_trends
        )
    except IndexError:
        pass  # no content yet

    return Content.objects.filter(pk__in=content_pks)
