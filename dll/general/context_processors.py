from django.contrib.sites.models import Site


def platform_variables(request):
    site = Site.objects.get_current()
    if site.id == 1:
        return {
            "main_js": "main_dll",
            "main_css": "main_dll",
            "template_suffix": "dll",
            "title": "digital.learning.lab",
        }
    elif site.id == 2:
        return {
            "main_js": "main_dlt",
            "main_css": "main_dlt",
            "template_suffix": "dlt",
            "title": "digital.learning.tools",
        }
