from django.contrib import admin

# Register your models here.
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from dll.content.forms import FlatPageAdminForm, HelpTextAdminForm
from .models import TeachingModule, Competence, SubCompetence, Trend, Tool, HelpText

admin.site.unregister(FlatPage)


@admin.register(TeachingModule, Trend, Tool)
class ContentAdmin(admin.ModelAdmin):
    exclude = ('json_data',)


@admin.register(HelpText)
class HelpTextAdmin(admin.ModelAdmin):
    form = HelpTextAdminForm

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(HelpTextAdmin, self).get_fieldsets(request, obj)
        if obj:
            for key in obj.json_data.keys():
                fieldsets[0][1]['fields'].append(key)
        return fieldsets


@admin.register(FlatPage)
class FlatPageAdmin(FlatPageAdmin):
    form = FlatPageAdminForm


admin.site.register(Competence)
admin.site.register(SubCompetence)
