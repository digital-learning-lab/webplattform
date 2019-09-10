# -*- coding: utf-8 -*-
import csv

from django.core.management import BaseCommand

from dll.communication.models import NewsletterSubscrption


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('dll/fixtures/newsletter.csv') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                obj = NewsletterSubscrption.objects.update_or_create(
                    email=row[0]
                )
