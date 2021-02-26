from django.db import migrations


def forward_func(apps, schema_editor):
    FlatMenu = apps.get_model("wagtailmenus", "FlatMenu")
    FlatMenuItem = apps.get_model("wagtailmenus", "FlatMenuItem")

    flat_menu = FlatMenu.objects.create(
        site=1, title="digital.learning.lab Menu", handle="menu", heading=""
    )

    items = [
        {"link_url": "/", "url_append": "#dll-aufbau", "link_text": "Was ist das dll?"},
        {"link_url": "/kontakt", "url_append": "", "link_text": "Kontakt"},
        {"link_url": "/newsletter", "url_append": "", "link_text": "Newsletter"},
        {"link_url": "/faq", "url_append": "", "link_text": "FAQ"},
    ]

    for item in items:
        FlatMenuItem.objects.create(
            link_url=item["link_url"],
            url_append=item["url_append"],
            link_text=item["link_text"],
            menu=flat_menu,
        )


def backwards_func(apps, schema_editor):
    FlatMenu = apps.get_model("wagtailmenus", "FlatMenu")
    FlatMenu.objects.get(handle="menu").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0005_create_change_email_event_type"),
    ]

    operations = [migrations.RunPython(forward_func, backwards_func)]
