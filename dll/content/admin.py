from django.contrib import admin

# Register your models here.
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from dll.content.forms import FlatPageAdminForm
from .models import TeachingModule, Competence, SubCompetence, Trend, Tool


admin.site.unregister(FlatPage)


@admin.register(TeachingModule, Trend, Tool)
class ContentAdmin(admin.ModelAdmin):
    exclude = ('json_data',)


@admin.register(FlatPage)
class FlatPageAdmin(FlatPageAdmin):
    form = FlatPageAdminForm

admin.site.register(Competence)
admin.site.register(SubCompetence)
