import rules
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from dll.general.models import DllSlugField


class DllUserManager(BaseUserManager):
    """
    copies the functionality of the default UserManager, but allows to create users without a username
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class DllUser(AbstractUser):
    email = models.EmailField(_('email address'), blank=True, unique=True)
    username = models.CharField(
        _('username'),
        max_length=150,
        null=True
    )
    doi_confirmed = models.BooleanField(
        _('Double-opt-in confirmed'),
        default=False,
    )

    slug = DllSlugField(populate_from='username')
    json_data = JSONField(default=dict)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = DllUserManager()

    def __str__(self):
        return f'{self.username} - {self.full_name} - ({self.email})'

    @cached_property
    def full_name(self):
        if self.first_name or self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.username

    def qs_of_personal_content(self):
        from dll.content.models import Content
        return Content.objects.filter(author=self)

    def qs_of_coauthored_content(self):
        return self.collaborative_content.filter(co_authors=self)

    def qs_any_content(self):
        return list(self.qs_of_personal_content()) + list(self.qs_of_coauthored_content())

    @property
    def is_reviewer(self):
        return self.is_superuser or rules.is_group_member('BSB-Reviewer')(self) or \
               rules.is_group_member('TUHH-Reviewer')(self)
