from django.contrib import admin

# Register your models here.
from .models import TeachingModule, Competence, SubCompetence, Trend, Tool


@admin.register(TeachingModule, Trend, Tool)
class ContentAdmin(admin.ModelAdmin):
    exclude = ('json_data',)


admin.site.register(Competence)
admin.site.register(SubCompetence)
