from django.contrib.auth.models import AbstractUser
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

    gender = models.CharField(max_length=10, choices=GENDER_OPTIONS)
    doi_confirmed = models.BooleanField(
        _('Double-opt-in confirmed'),
        default=False,
    )
    profile_image = FilerImageField(null=True, blank=True, on_delete=models.CASCADE)
    slug = DllSlugField(populate_from='username')
    json_data = JSONField(default=dict)

    @property
    def get_profile_image(self):
        # TODO: default images depending on gender
        return None
