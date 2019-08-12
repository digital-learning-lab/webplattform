from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from filer.fields.image import FilerImageField
from django.utils.translation import ugettext_lazy as _

from dll.general.models import DllSlugField


class DllUser(AbstractUser):
    GENDER_OPTIONS = (
        ('male', _("Männlich")),
        ('female', _("Weiblich")),
    )

    email = models.EmailField(_('email address'), blank=True, unique=True)

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

    @property
    def get_profile_image(self):
        # TODO: default images depending on gender
        return None

    def qs_of_personal_content(self):
        from dll.content.models import Content
        return Content.objects.filter(author=self)

    def qs_of_coauthored_content(self):
        return self.collaborative_content.filter(co_authors=self)
