from django.db import migrations


def forward_func(apps, schema_editor):
    CommunicationEventType = apps.get_model("communication", "CommunicationEventType")
    CommunicationEventType.objects.create(
        code="TESTIMONIAL_SUBMITTED_FOR_REVIEW", name="Erfahrungsbericht eingericht"
    )


def backwards_func(apps, schema_editor):
    CommunicationEventType = apps.get_model("communication", "CommunicationEventType")
    try:
        CommunicationEventType.objects.get(
            code="TESTIMONIAL_SUBMITTED_FOR_REVIEW"
        ).delete()
    except CommunicationEventType.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ("communication", "0031_testimonialreview"),
    ]

    operations = [migrations.RunPython(forward_func, backwards_func)]
