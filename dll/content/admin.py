from django.contrib import admin

# Register your models here.
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from dll.content.forms import FlatPageAdminForm, HelpTextAdminForm, HelpTextFieldForm
from .models import TeachingModule, Competence, SubCompetence, Trend, Tool, HelpText, HelpTextField

admin.site.unregister(FlatPage)


@admin.register(TeachingModule, Trend, Tool)
class ContentAdmin(admin.ModelAdmin):
    exclude = ('json_data',)


class HelpTextFieldInline(admin.TabularInline):
    model = HelpTextField
    form = HelpTextFieldForm

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 1
        else:
            return 0

    def has_add_permission(self, request, obj=None):
        if obj:
            return True
        else:
            return False

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(HelpTextFieldInline, self).get_formset(request, obj, **kwargs)
        return formset


@admin.register(HelpText)
class HelpTextAdmin(admin.ModelAdmin):
    form = HelpTextAdminForm
    inlines = [HelpTextFieldInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            readonly_fields = self.readonly_fields
            readonly_fields += ('content_type',)
            return readonly_fields
        else:
            return self.readonly_fields


@admin.register(FlatPage)
class FlatPageAdmin(FlatPageAdmin):
    form = FlatPageAdminForm


admin.site.register(Competence)
admin.site.register(SubCompetence)
