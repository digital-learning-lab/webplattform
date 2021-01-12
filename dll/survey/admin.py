from django.contrib import admin

import nested_admin

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
    inlines = [SurveyQuestionInlineAdmin]


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
