from django.db import migrations


def forward_func(apps, schema_editor):
    FlatMenu = apps.get_model("wagtailmenus", "FlatMenu")
    FlatMenuItem = apps.get_model("wagtailmenus", "FlatMenuItem")

    guest_menu = FlatMenu.objects.create(
        site_id=1, title="Navigation - Guest", handle="guest_menu", heading=""
    )

    logged_in_menu = FlatMenu.objects.create(
        site_id=1, title="Navigation - Logged In", handle="logged_in_menu", heading=""
    )

    reviewer_menu = FlatMenu.objects.create(
        site_id=1, title="Navigation - Reviewer", handle="reviewer_menu", heading=""
    )

    guest_items = [
        {"link_url": "/", "url_append": "", "link_text": "Home"},
        {"link_url": "/login", "url_append": "", "link_text": "Login"},
        {"link_url": "/", "url_append": "#dll-aufbau", "link_text": "Was ist das dll?"},
        {"link_url": "/kontakt", "url_append": "", "link_text": "Kontakt"},
        {"link_url": "/newsletter", "url_append": "", "link_text": "Newsletter"},
        {"link_url": "/faq", "url_append": "", "link_text": "FAQ"},
    ]

    logged_in_items = [
        {"link_url": "/", "url_append": "", "link_text": "Home"},
        {"link_url": "/profil/", "url_append": "", "link_text": "Mein Profil"},
        {
            "link_url": "/mein-merkzettel",
            "url_append": "",
            "link_text": "Mein Merkzettel",
        },
        {"link_url": "/meine-inhalte", "url_append": "", "link_text": "Meine Inhalte"},
        {"link_url": "/", "url_append": "#dll-aufbau", "link_text": "Was ist das dll?"},
        {"link_url": "/kontakt", "url_append": "", "link_text": "Kontakt"},
        {"link_url": "/newsletter", "url_append": "", "link_text": "Newsletter"},
        {"link_url": "/faq", "url_append": "", "link_text": "FAQ"},
        {"link_url": "/logout/", "url_append": "", "link_text": "Logout"},
    ]

    reviewer_items = [
        {"link_url": "/", "url_append": "", "link_text": "Home"},
        {"link_url": "/profil/", "url_append": "", "link_text": "Mein Profil"},
        {
            "link_url": "/mein-merkzettel",
            "url_append": "",
            "link_text": "Mein Merkzettel",
        },
        {"link_url": "/meine-inhalte", "url_append": "", "link_text": "Meine Inhalte"},
        {
            "link_url": "/review-inhalte",
            "url_append": "",
            "link_text": "Review Inhalte",
        },
        {"link_url": "/", "url_append": "#dll-aufbau", "link_text": "Was ist das dll?"},
        {"link_url": "/kontakt", "url_append": "", "link_text": "Kontakt"},
        {"link_url": "/newsletter", "url_append": "", "link_text": "Newsletter"},
        {"link_url": "/faq", "url_append": "", "link_text": "FAQ"},
        {"link_url": "/logout/", "url_append": "", "link_text": "Logout"},
    ]

    for item in guest_items:
        FlatMenuItem.objects.create(
            link_url=item["link_url"],
            url_append=item["url_append"],
            link_text=item["link_text"],
            menu=guest_menu,
        )

    for item in logged_in_items:
        FlatMenuItem.objects.create(
            link_url=item["link_url"],
            url_append=item["url_append"],
            link_text=item["link_text"],
            menu=logged_in_menu,
        )

    for item in reviewer_items:
        FlatMenuItem.objects.create(
            link_url=item["link_url"],
            url_append=item["url_append"],
            link_text=item["link_text"],
            menu=reviewer_menu,
        )


def backwards_func(apps, schema_editor):
    FlatMenu = apps.get_model("wagtailmenus", "FlatMenu")
    FlatMenu.objects.get(handle="guest_menu").delete()
    FlatMenu.objects.get(handle="logged_in_menu").delete()
    FlatMenu.objects.get(handle="reviewer_menu").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0004_auto_20201217_1835"),
        ("wagtailmenus", "0023_remove_use_specific"),
    ]

    operations = [migrations.RunPython(forward_func, backwards_func)]
