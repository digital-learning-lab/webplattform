from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission


def get_bsb_reviewer_group():
    group, created = Group.objects.get_or_create(name="BSB-Reviewer")
    return group


def get_tuhh_reviewer_group():
    group, created = Group.objects.get_or_create(name="TUHH-Reviewer")
    return group


def get_author_group():
    group, created = Group.objects.get_or_create(name="Author")
    return group


def get_default_tuhh_user():
    user, created = get_user_model().objects.get_or_create(
        username=settings.DEFAULT_USER_EMAIL, email=settings.DEFAULT_USER_EMAIL
    )
    if created:
        user.set_password(settings.DEFAULT_USER_PASSWORD)
    user.is_superuser = True
    user.first_name = "TUHH"
    user.save()
    return user
