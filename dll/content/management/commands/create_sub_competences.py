# -*- coding: utf-8 -*-
from django.core.management import BaseCommand

from dll.content.models import SubCompetence


class Command(BaseCommand):

    def handle(self, *args, **options):
        for sub_competence in SubCompetence.DEFAULT_NAMES:
            ordering = int(str(sub_competence[0]).ljust(4, '0'))
            SubCompetence.objects.get_or_create(cid=sub_competence[0], ordering=ordering)
