from django.db import migrations


def forward_func(apps, schema_editor):
    CommunicationEventType = apps.get_model("communication", "CommunicationEventType")
    CommunicationEventType.objects.create(
        code="USER_EMAIL_CHANGE", name="Nutzer E-Mail Adresse ändern."
    )


def backwards_func(apps, schema_editor):
    CommunicationEventType = apps.get_model("communication", "CommunicationEventType")
    try:
        CommunicationEventType.objects.get(code="USER_EMAIL_CHANGE").delete()
    except CommunicationEventType.DoesNotExist:
        pass


class Migration(migrations.Migration):
    dependencies = [
        ("communication", "0004_create_user_password_reset_event_type"),
    ]

    operations = [migrations.RunPython(forward_func, backwards_func)]
