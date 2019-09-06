# -*- coding: utf-8 -*-
import json

from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from dll.content.models import HelpText, HelpTextField


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('dll/fixtures/help_texts.json') as json_file:
            data = json.load(json_file)
            for help_text_dict in data['list']:
                app_label, model = help_text_dict['content_type'].split('.')
                ct = ContentType.objects.get(
                    app_label=app_label,
                    model=model
                )
                help_text, created = HelpText.objects.get_or_create(content_type=ct)
                for field in help_text_dict['fields']:
                    HelpTextField.objects.get_or_create(
                        name=field['name'],
                        help_text=help_text,
                        text=field['text'],
                    )
