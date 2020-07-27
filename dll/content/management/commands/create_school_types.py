# -*- coding: utf-8 -*-
from django.core.management import BaseCommand

from dll.content.models import SchoolType

SCHOOL_TYPES = [
    "Grundschule",
    "Werkrealschule",
    "Hauptschule",
    "Realschule",
    "Gemeinschaftsschule",
    "Gymnasium",
    "Mittelschule",
    "Integrierte Sekundarschule (ISS)",
    "Gesamtschule",
    "Oberschule",
    "Werkschule",
    "Mittelstufenschule",
    "Regionale Schule",
    "Integrierte Gesamtschule",
    "Realschulen plus",
    "Sekundarschule",
    "Regelschule",
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for school_type in SCHOOL_TYPES:
            SchoolType.objects.get_or_create(name=school_type)
