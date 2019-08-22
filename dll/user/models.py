from django.contrib.auth.models import AbstractUser, Group
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from dll.general.models import DllSlugField


class DllUser(AbstractUser):
    GENDER_OPTIONS = (
        ('male', _("Männlich")),
        ('female', _("Weiblich")),
    )

    email = models.EmailField(_('email address'), blank=True, unique=True)
    username = models.CharField(
        _('username'),
        max_length=150,
        null=True
    )
    gender = models.CharField(max_length=10, choices=GENDER_OPTIONS)
    doi_confirmed = models.BooleanField(
        _('Double-opt-in confirmed'),
        default=False,
    )

    slug = DllSlugField(populate_from='username')
    json_data = JSONField(default=dict)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'gender']

    def __str__(self):
        return f'{self.username} - {self.full_name} - ({self.email})'

    @cached_property
    def full_name(self):
        return f'{self.username}'
        # TODO importer
        # return f'{self.first_name} {self.last_name}'

    def qs_of_personal_content(self):
        from dll.content.models import Content
        return Content.objects.filter(author=self)

    def qs_of_coauthored_content(self):
        return self.collaborative_content.filter(co_authors=self)

    def qs_any_content(self):
        return list(self.qs_of_personal_content()) + list(self.qs_of_coauthored_content())
