# -*- coding: utf-8 -*-
from django.core.management import BaseCommand

from dll.user.models import DllUser


USERS = [
    {
        "username": "admin",
        "email": "admin@tuhh.de",
        "password": "test1234!",
        "is_staff": True,
        "is_superuser": True,
        "is_active": True,
    },
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in USERS:
            DllUser.objects.create_superuser(**user)
