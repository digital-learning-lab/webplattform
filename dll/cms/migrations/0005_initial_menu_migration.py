from django.db import migrations


def forward_func(apps, schema_editor):
    FlatMenu = apps.get_model("wagtailmenus", "FlatMenu")
    FlatMenuItem = apps.get_model("wagtailmenus", "FlatMenuItem")
    Site = apps.get_model("wagtailcore", "Site")

    site = Site.objects.first()

    guest_menu = FlatMenu.objects.create(
        site_id=site.pk, title="Navigation - Guest", handle="guest_menu", heading=""
    )

    logged_in_menu = FlatMenu.objects.create(
        site_id=site.pk,
        title="Navigation - Logged In",
        handle="logged_in_menu",
        heading="",
    )

    reviewer_menu = FlatMenu.objects.create(
        site_id=site.pk,
        title="Navigation - Reviewer",
        handle="reviewer_menu",
        heading="",
    )

    guest_items = [
        {"link_url": "/", "url_append": "", "link_text": "Home", "sort_order": 0},
        {"link_url": "/login", "url_append": "", "link_text": "Login", "sort_order": 1},
        {
            "link_url": "/",
            "url_append": "#dll-aufbau",
            "link_text": "Was ist das dll?",
            "sort_order": 2,
        },
        {
            "link_url": "/kontakt",
            "url_append": "",
            "link_text": "Kontakt",
            "sort_order": 3,
        },
        {
            "link_url": "/newsletter",
            "url_append": "",
            "link_text": "Newsletter",
            "sort_order": 4,
        },
        {"link_url": "/faq", "url_append": "", "link_text": "FAQ", "sort_order": 5},
    ]

    logged_in_items = [
        {"link_url": "/", "url_append": "", "link_text": "Home", "sort_order": 0},
        {
            "link_url": "/profil/",
            "url_append": "",
            "link_text": "Mein Profil",
            "sort_order": 1,
        },
        {
            "link_url": "/mein-merkzettel",
            "url_append": "",
            "link_text": "Mein Merkzettel",
            "sort_order": 2,
        },
        {
            "link_url": "/meine-inhalte",
            "url_append": "",
            "link_text": "Meine Inhalte",
            "sort_order": 3,
        },
        {
            "link_url": "/",
            "url_append": "#dll-aufbau",
            "link_text": "Was ist das dll?",
            "sort_order": 4,
        },
        {
            "link_url": "/kontakt",
            "url_append": "",
            "link_text": "Kontakt",
            "sort_order": 5,
        },
        {
            "link_url": "/newsletter",
            "url_append": "",
            "link_text": "Newsletter",
            "sort_order": 6,
        },
        {"link_url": "/faq", "url_append": "", "link_text": "FAQ", "sort_order": 7},
        {
            "link_url": "/logout/",
            "url_append": "",
            "link_text": "Logout",
            "sort_order": 8,
        },
    ]

    reviewer_items = [
        {"link_url": "/", "url_append": "", "link_text": "Home", "sort_order": 0},
        {
            "link_url": "/profil/",
            "url_append": "",
            "link_text": "Mein Profil",
            "sort_order": 1,
        },
        {
            "link_url": "/mein-merkzettel",
            "url_append": "",
            "link_text": "Mein Merkzettel",
            "sort_order": 2,
        },
        {
            "link_url": "/meine-inhalte",
            "url_append": "",
            "link_text": "Meine Inhalte",
            "sort_order": 3,
        },
        {
            "link_url": "/review-inhalte",
            "url_append": "",
            "link_text": "Review Inhalte",
            "sort_order": 4,
        },
        {
            "link_url": "/",
            "url_append": "#dll-aufbau",
            "link_text": "Was ist das dll?",
            "sort_order": 5,
        },
        {
            "link_url": "/kontakt",
            "url_append": "",
            "link_text": "Kontakt",
            "sort_order": 6,
        },
        {
            "link_url": "/newsletter",
            "url_append": "",
            "link_text": "Newsletter",
            "sort_order": 7,
        },
        {"link_url": "/faq", "url_append": "", "link_text": "FAQ", "sort_order": 8},
        {
            "link_url": "/logout/",
            "url_append": "",
            "link_text": "Logout",
            "sort_order": 9,
        },
    ]

    guest_items.reverse()
    logged_in_items.reverse()
    reviewer_items.reverse()

    for item in guest_items:
        FlatMenuItem.objects.create(
            link_url=item["link_url"],
            url_append=item["url_append"],
            link_text=item["link_text"],
            menu=guest_menu,
            sort_order=item["sort_order"],
        )

    for item in logged_in_items:
        FlatMenuItem.objects.create(
            link_url=item["link_url"],
            url_append=item["url_append"],
            link_text=item["link_text"],
            menu=logged_in_menu,
            sort_order=item["sort_order"],
        )

    for item in reviewer_items:
        FlatMenuItem.objects.create(
            link_url=item["link_url"],
            url_append=item["url_append"],
            link_text=item["link_text"],
            menu=reviewer_menu,
            sort_order=item["sort_order"],
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
