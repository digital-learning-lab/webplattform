from django.db import migrations


def forward_func(apps, schema_editor):
    CommunicationEventType = apps.get_model("communication", "CommunicationEventType")
    CommunicationEventType.objects.create(
        code="TESTIMONIAL_SUBMITTED_FOR_REVIEW", name="Erfahrungsbericht eingericht"
    )

    CommunicationEventType.objects.create(
        code="TESTIMONIAL_REVIEW_DONE", name="Erfahrungsbericht aktualisiert"
    )


def backwards_func(apps, schema_editor):
    CommunicationEventType = apps.get_model("communication", "CommunicationEventType")
    try:
        CommunicationEventType.objects.get(
            code="TESTIMONIAL_SUBMITTED_FOR_REVIEW"
        ).delete()
    except CommunicationEventType.DoesNotExist:
        pass

    try:
        CommunicationEventType.objects.get(code="TESTIMONIAL_REVIEW_DONE").delete()
    except CommunicationEventType.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ("communication", "0007_alter_communicationeventtype_from_email"),
    ]

    operations = [migrations.RunPython(forward_func, backwards_func)]
