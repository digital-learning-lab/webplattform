# Generated by Django 3.2.15 on 2022-10-05 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("communication", "0006_auto_20220929_1014"),
    ]

    operations = [
        migrations.AlterField(
            model_name="communicationeventtype",
            name="from_email",
            field=models.EmailField(
                default="digital.learning.lab@tuhh.de", max_length=128
            ),
        ),
    ]