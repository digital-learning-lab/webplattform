from constance import config

from django.contrib.sites.models import Site


def platform_variables(request):
    site = Site.objects.get_current()
    DLT_FEATURES_ENABLED = config.DLL_ENABLE_DLT_FEATURES
    DEFAULTS = {
        "request": request,
        "main_js": "main_dll",
        "main_css": "main_dll",
        "template_suffix": "dll",
        "title": "digital.learning.lab",
        "dll_logo": "img/logo/dll_logo_rgb_claim_rechts.png",
        "dlt_logo": "img/logo/logo_dlt.svg",
        "logo_desktop_1x": "img/logo/dll_logo_rgb_claim_rechts.png",
        "logo_desktop_2x": "img/logo/dll_logo_rgb_claim_rechts_large.png",
        "logo_mobile_1x": "img/logo/dll_logo_rgb_ohne_claim.png",
        "logo_mobile_2x": "img/logo/dll_logo_rgb_ohne_claim_large.png",
        "SITE_ID": 1,
        "DLT_FEATURES_ENABLED": DLT_FEATURES_ENABLED,
        "cookiebanner_duration": config.DURATION,
        "cookiebanner_message": config.MESSAGE,
        "cookiebanner_button_text": config.BUTTON_TEXT,
    }
    try:
        DEFAULTS.update(
            {
                "dll_url": f"https://{Site.objects.get(id=1).domain}",
                "dlt_url": f"https://{Site.objects.get(id=2).domain}",
            }
        )
    except Site.DoesNotExist:
        pass

    if site.id == 2:
        DEFAULTS.update(
            {
                "main_js": "main_dlt",
                "main_css": "main_dlt",
                "template_suffix": "dlt",
                "title": "digital.learning.tools",
                "logo_desktop_1x": "img/logo/logo_dlt.svg",
                "logo_desktop_2x": "img/logo/logo_dlt.svg",
                "dlt_logo": "img/logo/logo_dlt.svg",
                "logo_mobile_1x": "img/logo/logo_dlt_mobile.svg",
                "logo_mobile_2x": "img/logo/logo_dlt_mobile.svg",
                "SITE_ID": 2,
                "DLT_FEATURES_ENABLED": DLT_FEATURES_ENABLED,
            }
        )
    return DEFAULTS
