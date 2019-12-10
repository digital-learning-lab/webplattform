from functools import update_wrapper

from django.contrib import admin, messages

from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.core.management import call_command
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.urls import path

from dll.content.forms import FlatPageAdminForm, HelpTextAdminForm, HelpTextFieldForm
from .models import TeachingModule, Competence, OperatingSystem, SubCompetence, Subject, SchoolType, Trend, Tool, ToolApplication, HelpText, HelpTextField

admin.site.unregister(FlatPage)


@admin.register(TeachingModule, Trend)
class ContentAdmin(admin.ModelAdmin):
    exclude = ('json_data',)


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super(ToolAdmin, self).get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        custom_urls = [
            path('remove-tools-without-name', wrap(self._remove_tools_without_name), name="cleanup_tools"),
        ]
        return urls + custom_urls

    def _remove_tools_without_name(self, request):
        call_command('cleanup_broken_tools')
        messages.add_message(request, messages.INFO, _('Deleted all tools without a name.'))
        return redirect('admin:content_tool_changelist')


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


def download_as_json(modeladmin, request, queryset):
    result = {
        'list': []
    }
    for help_text in queryset:
        help_text_json = {}
        help_text_json['content_type'] = help_text.content_type.app_label + '.' + help_text.content_type.model
        help_text_json['fields'] = []
        for field in help_text.help_text_fields.all():
            help_text_json['fields'].append({
                'name': field.name,
                'text': field.text
            })
        result['list'].append(help_text_json)
    return JsonResponse(result)


@admin.register(HelpText)
class HelpTextAdmin(admin.ModelAdmin):
    form = HelpTextAdminForm
    inlines = [HelpTextFieldInline]
    actions = [download_as_json]

    class Media:
        js = (
            '//cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js',
            '//cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js',
        )

        css = {
            'all': ('//cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css',)
        }


@admin.register(FlatPage)
class FlatPageAdmin(FlatPageAdmin):
    form = FlatPageAdminForm


admin.site.register(Competence)
admin.site.register(SubCompetence)
admin.site.register(Subject)
admin.site.register(SchoolType)
admin.site.register(OperatingSystem)
admin.site.register(ToolApplication)

