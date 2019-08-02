from django.contrib import admin

# Register your models here.
from .models import TeachingModule, Competence, SubCompetence, Trend, Tool

admin.site.register(TeachingModule)
admin.site.register(Trend)
admin.site.register(Tool)
admin.site.register(Competence)
admin.site.register(SubCompetence)
