# Generated by Django 3.2.15 on 2022-10-19 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0026_auto_20221019_1417"),
    ]

    operations = [
        migrations.AlterField(
            model_name="testimonial",
            name="content",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="testimonials",
                related_query_name="testimonial",
                to="content.content",
                verbose_name="Content",
            ),
        ),
    ]
