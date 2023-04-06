# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand

from dll.content.models import Tool


class Command(BaseCommand):
    def handle(self, *args, **options):
        for t in Tool.objects.all():
            for f in t.functions.all():
                try:
                    t.potentials.add(f.potential)
                except ObjectDoesNotExist:
                    pass
            t.save()
