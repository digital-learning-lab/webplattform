from django.db import migrations


def add_tool_potentials(apps, schema_editor):
    Potential = apps.get_model("content", "Potential")
    titles = [
        "Visualisieren, Animieren und Simulieren",
        "Kommunizieren",
        "Inhalte teilen",
        "Zusammenarbeiten und Kooperieren",
        "Reflektieren",
        "Strukturieren und Systematisieren",
        "Testen und Bewerten",
        "Spielerisch lernen",
        "Inhalte produzieren",
        "Probleme lösen",
    ]
    for title in titles:
        Potential.objects.create(name=title)


def remove_tool_potentials(apps, schema_editor):
    Potential = apps.get_model("content", "Potential")
    Potential.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0023_auto_20221005_2244"),
    ]

    operations = [migrations.RunPython(add_tool_potentials, remove_tool_potentials)]
