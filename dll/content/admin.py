import xlsxwriter
from django.contrib import admin

from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.http import JsonResponse, HttpResponse
from django.utils.six import BytesIO
from django.utils.translation import ugettext_lazy as _

from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from import_export import resources
from import_export.admin import ImportExportMixin

from dll.content.forms import FlatPageAdminForm, HelpTextAdminForm, HelpTextFieldForm
from .models import (
    TeachingModule,
    Competence,
    OperatingSystem,
    SubCompetence,
    Subject,
    SchoolType,
    Trend,
    Tool,
    ToolApplication,
    HelpText,
    HelpTextField,
    ContentLink,
    ToolFunction,
    CompetenceAdditionalInformation,
)

admin.site.unregister(FlatPage)


class TeachingModuleResource(resources.ModelResource):
    def after_save_instance(self, instance, using_transactions, dry_run):
        if instance.publisher_linked and not dry_run:
            published = instance.publisher_linked.get_real_instance()
            published.hybrid = instance.hybrid
            published.save()

    class Meta:
        model = TeachingModule
        skip_unchanged = True
        report_skipped = True
        fields = ("id", "name", "hybrid")


class PublishedFilter(admin.SimpleListFilter):
    title = "Veröffentlicht"
    parameter_name = "publisher_is_draft"

    def lookups(self, request, model_admin):
        return (
            ("y", _("Yes")),
            ("n", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "y":
            return queryset.published()
        if self.value() == "n":
            return queryset.drafts()


class ContentLinkInlineAdmin(admin.StackedInline):
    model = ContentLink


class CompetenceAdditionalInformationInlineAdmin(admin.StackedInline):
    model = CompetenceAdditionalInformation
    max_num = 1
    min_num = 1


@admin.register(Trend)
class ContentAdmin(admin.ModelAdmin, DynamicArrayMixin):
    exclude = ("json_data", "tags")
    inlines = [ContentLinkInlineAdmin]


@admin.register(TeachingModule)
class TeachingModuleAdmin(ImportExportMixin, ContentAdmin):
    actions = ["export_xlsx"]
    list_filter = (PublishedFilter,)
    resource_class = TeachingModuleResource

    def get_export_queryset(self, request):
        qs = super(TeachingModuleAdmin, self).get_export_queryset(request)
        return qs.drafts()

    def export_xlsx(self, request, queryset):

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        worksheet.write_row(
            0,
            0,
            [
                "Titel",
                "Autor_in",
                "Hochladedatum",
                "KMK - Kompetenz",
                "mind. Unterrichtsstufe",
                "max. Unterrichtsstufe ",
                "Zeitaufwand",
                "Schulform",
                "Bildungsplanbezug",
                "Verlinkte Tools",
                "Verlinkte Trends",
            ],
        )
        counter = 1
        for tm in queryset:
            worksheet.write_row(
                counter,
                0,
                [
                    tm.name,
                    tm.author.full_name if tm.author else "",
                    tm.created.strftime("%d.%m.%Y") if tm.created else "",
                    ", ".join([c.name for c in tm.competences.all()]),
                    tm.school_class.lower if tm.school_class else "",
                    tm.school_class.upper if tm.school_class else "",
                    tm.estimated_time,
                    ", ".join([t.name for t in tm.school_types.all()]),
                    tm.educational_plan_reference,
                    ", ".join([t.name for t in tm.related_tools.all()]),
                    ", ".join([t.name for t in tm.related_trends.all()]),
                ],
            )
            counter += 1

        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response[
            "Content-Disposition"
        ] = "attachment; filename=unterrichtsbausteine.xlsx"

        return response

    export_xlsx.short_description = "Unterrichtsbausteine als XLSX exportieren"


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    exclude = ("json_data", "tags")


class HelpTextFieldInline(admin.TabularInline):
    model = HelpTextField
    form = HelpTextFieldForm

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 1
        else:
            return 0

    def has_add_permission(self, request, obj=None):
        return bool(obj)


def download_as_json(modeladmin, request, queryset):
    result = {"list": []}
    for help_text in queryset:
        help_text_json = {
            "content_type": help_text.content_type.app_label
            + "."
            + help_text.content_type.model,
            "fields": [],
        }

        for field in help_text.help_text_fields.all():
            help_text_json["fields"].append({"name": field.name, "text": field.text})
        result["list"].append(help_text_json)
    return JsonResponse(result)


@admin.register(HelpText)
class HelpTextAdmin(admin.ModelAdmin):
    form = HelpTextAdminForm
    inlines = [HelpTextFieldInline]
    actions = [download_as_json]

    class Media:
        js = (
            "//cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js",
            "//cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js",
        )

        css = {
            "all": (
                "//cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
            )
        }


@admin.register(FlatPage)
class FlatPageAdmin(FlatPageAdmin):
    form = FlatPageAdminForm


@admin.register(Competence)
class CompetenceAdmin(admin.ModelAdmin):
    inlines = [CompetenceAdditionalInformationInlineAdmin]


admin.site.register(ToolFunction)
admin.site.register(SubCompetence)
admin.site.register(Subject)
admin.site.register(SchoolType)
admin.site.register(OperatingSystem)
admin.site.register(ToolApplication)
