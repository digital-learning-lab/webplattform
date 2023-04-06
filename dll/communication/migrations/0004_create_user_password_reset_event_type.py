from django.db import migrations


def forward_func(apps, schema_editor):
    CommunicationEventType = apps.get_model("communication", "CommunicationEventType")
    CommunicationEventType.objects.create(
        code="USER_PASSWORD_RESET", name="Nutzer Passwort Reset E-Mail"
    )


def backwards_func(apps, schema_editor):
    CommunicationEventType = apps.get_model("communication", "CommunicationEventType")
    try:
        CommunicationEventType.objects.get(code="USER_PASSWORD_RESET").delete()
    except CommunicationEventType.DoesNotExist:
        pass


class Migration(migrations.Migration):
    dependencies = [
        ("communication", "0003_auto_20200113_1540"),
    ]

    operations = [migrations.RunPython(forward_func, backwards_func)]
