# -*- coding: utf-8 -*-
from django.core.management import BaseCommand

from dll.content.models import Subject

SUBJECTS = [
    "Arbeit und Beruf",
    "Bildende Kunst",
    "Biologie",
    "Chemie",
    "Deutsch",
    "Deutsch als Zweitsprache",
    "Englisch",
    "Französisch",
    "Fremdsprachen",
    "Geographie",
    "Geschichte",
    "Gesellschaft",
    "Informatik",
    "Kunst",
    "Latein",
    "Mathematik",
    "Musik",
    "Naturwissenschaft und Technik",
    "Niederdeutsch",
    "Philosophie",
    "Physik",
    "Politik",
    "Politik/Gesellschaft/Wirtschaft",
    "Religion",
    "Sachunterricht",
    "Spanisch",
    "Sport",
    "Theater",
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for subject in SUBJECTS:
            Subject.objects.get_or_create(name=subject)
