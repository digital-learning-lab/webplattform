from django.contrib.sites.models import Site


def platform_variables(request):
    site = Site.objects.get_current()
    DEFAULTS = {
        "main_js": "main_dll",
        "main_css": "main_dll",
        "template_suffix": "dll",
        "title": "digital.learning.lab",
        "logo_desktop_1x": "img/logo/dll_logo_rgb_claim_rechts.png",
        "logo_desktop_2x": "img/logo/dll_logo_rgb_claim_rechts_large.png",
        "logo_mobile_1x": "img/logo/dll_logo_rgb_ohne_claim.png",
        "logo_mobile_2x": "img/logo/dll_logo_rgb_ohne_claim_large.png",
    }
    if site.id == 1:
        return DEFAULTS
    elif site.id == 2:
        return {
            "main_js": "main_dlt",
            "main_css": "main_dlt",
            "template_suffix": "dlt",
            "title": "digital.learning.tools",
            "logo_desktop_1x": "img/logo/logo_dlt.svg",
            "logo_desktop_2x": "img/logo/logo_dlt.svg",
            "logo_mobile_1x": "img/logo/logo_dlt_mobile.svg",
            "logo_mobile_2x": "img/logo/logo_dlt_mobile.svg",
        }
    return DEFAULTS
