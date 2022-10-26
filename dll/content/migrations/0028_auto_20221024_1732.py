# Generated by Django 3.2.15 on 2022-10-24 15:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
        ("content", "0027_alter_testimonial_content"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataprivacyassessment",
            name="overall",
            field=models.CharField(
                choices=[
                    ("compliant", "Compliant"),
                    ("not_compliant", "Not Compliant"),
                    ("unknown", "Unknown"),
                ],
                max_length=32,
                null=True,
                verbose_name="Gesamteindruck",
            ),
        ),
        migrations.AlterField(
            model_name="content",
            name="site",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="sites.site"
            ),
        ),
        migrations.AlterField(
            model_name="historicalcontent",
            name="site",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                default=1,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="sites.site",
            ),
        ),
        migrations.AlterField(
            model_name="historicalteachingmodule",
            name="site",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                default=1,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="sites.site",
            ),
        ),
        migrations.AlterField(
            model_name="historicaltool",
            name="site",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                default=1,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="sites.site",
            ),
        ),
        migrations.AlterField(
            model_name="historicaltrend",
            name="site",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                default=1,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="sites.site",
            ),
        ),
    ]
