import xlsxwriter
from django.contrib import admin

import nested_admin
from django.http import HttpResponse
from django.utils.six import BytesIO

from dll.survey.models import (
    Trigger,
    Survey,
    SurveyResult,
    SurveyQuestion,
    SurveyQuestionChoice,
    SurveyResultAnswer,
)


class TriggerAdmin(admin.ModelAdmin):
    pass


class SurveyQuestionChoiceAdmin(nested_admin.NestedStackedInline):
    model = SurveyQuestionChoice
    sortable_field_name = "position"
    extra = 0
    min_num = 0


class SurveyQuestionInlineAdmin(nested_admin.NestedStackedInline):
    model = SurveyQuestion
    inlines = [SurveyQuestionChoiceAdmin]
    sortable_field_name = "position"
    extra = 0
    min_num = 1


class SurveyAdmin(nested_admin.NestedModelAdmin):
    actions = ["export_xlsx"]
    inlines = [SurveyQuestionInlineAdmin]

    def export_xlsx(self, request, queryset):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        survey = queryset.get()

        questions = [question.title for question in survey.survey_questions.all()]

        worksheet.write_row(0, 0, questions)
        for row, result in enumerate(
            SurveyResult.objects.filter(survey=survey), start=1
        ):
            k = []
            for question in survey.survey_questions.all():
                value = ""
                try:
                    value = SurveyResultAnswer.objects.get(
                        result_id=result.pk, question_id=question.pk
                    ).value
                except:
                    pass
                k.append(value)

            worksheet.write_row(row, 0, k)
        workbook.close()
        output.seek(0)

        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = "attachment; filename=umfrageergebnisse.xlsx"

        return response

    export_xlsx.short_description = "Umfrageergebnisse exportieren"


class SurveyResultAnswerInlineAdmin(admin.StackedInline):
    model = SurveyResultAnswer
    exclude = ["question"]
    readonly_fields = ["value"]
    extra = 0


class SurveyResultAdmin(admin.ModelAdmin):
    inlines = [SurveyResultAnswerInlineAdmin]


admin.site.register(Trigger, TriggerAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(SurveyResult, SurveyResultAdmin)
