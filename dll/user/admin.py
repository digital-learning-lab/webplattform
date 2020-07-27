from django.contrib import admin
from .models import DllUser


class DllUserAdmin(admin.ModelAdmin):
    exclude = ("json_data",)


admin.site.register(DllUser, DllUserAdmin)
