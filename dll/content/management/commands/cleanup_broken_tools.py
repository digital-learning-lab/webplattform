# -*- coding: utf-8 -*-
import logging

from django.core.management import BaseCommand

from dll.content.models import Tool
logger = logging.getLogger('dll.management')

class Command(BaseCommand):

    def handle(self, *args, **options):
        logger.info('Deleting tools without name.')
        Tool.objects.filter(name='').delete()
