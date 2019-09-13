# -*- coding: utf-8 -*-
import csv

from django.core.management import BaseCommand

from dll.communication.models import NewsletterSubscrption
from dll.content.utils import create_newsletter_subscriptions_from_csv


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('dll/fixtures/newsletter.csv') as csvfile:
            create_newsletter_subscriptions_from_csv(csvfile)
