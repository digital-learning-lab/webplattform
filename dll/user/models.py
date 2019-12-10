import rules
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel

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


class DllUser(TimeStampedModel, AbstractUser):
    email = models.EmailField(_('email address'), blank=True, unique=True)

    first_name = models.CharField(_('first name'), max_length=80, blank=True)

    username = models.CharField(
        _('username'),
        max_length=150,
        null=True
    )
    doi_confirmed = models.BooleanField(
        _('Double-opt-in confirmed'),
        default=False,
    )
    doi_confirmed_date = models.DateTimeField(
        _('Datum der Registrierungsbestätigung'),
        null=True,
        editable=False
    )

    slug = DllSlugField(populate_from='full_name')
    json_data = JSONField(default=dict)  # see README for details

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = DllUserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return f'{self.username} - {self.full_name} - ({self.email})'

    @cached_property
    def full_name(self):
        if self.first_name or self.last_name:
            return ' '.join(filter(None, [self.first_name, self.last_name]))
        if self.username:
            return self.username
        return ''

    def qs_of_personal_content(self):
        from dll.content.models import Content
        return Content.objects.filter(author=self)

    def qs_of_coauthored_content(self):
        return self.collaborative_content.filter(co_authors=self)

    def qs_any_content(self):
        return list(self.qs_of_personal_content()) + list(self.qs_of_coauthored_content())

    @property
    def is_reviewer(self):
        # todo: rewrite this as rule
        return self.is_superuser or rules.is_group_member('BSB-Reviewer')(self) or \
               rules.is_group_member('TUHH-Reviewer')(self)

    def retire(self):
        for content in self.qs_of_personal_content():
            content.author = None
            content.add_ex_author(self.full_name)

        for content in self.qs_of_coauthored_content():
            content.co_authors.remove(self)
            content.add_ex_author(self.full_name)

    @cached_property
    def status_list(self) -> list:
        status_list = []
        if self.is_superuser:
            status_list.append(_("Administrator"))
        if self.is_reviewer:
            status_list.append(_("Reviewer"))
        if self.is_active:
            status_list.append(_("Author"))
        return status_list


class EmailChangeRequest(TimeStampedModel):
    user = models.ForeignKey(DllUser, on_delete=models.CASCADE)
    email = models.EmailField()
