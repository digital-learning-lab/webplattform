# Generated by Django 2.2.9 on 2020-02-06 09:49

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('content', '0007_auto_20200123_1002'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='assigned_reviewer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_reviews', to=settings.AUTH_USER_MODEL, verbose_name='Assigned Reviewer'),
        ),
        migrations.AlterField(
            model_name='content',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, default=datetime.datetime(2020, 2, 6, 9, 49, 58, 520918, tzinfo=utc), null=True, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='contentlink',
            name='type',
            field=models.CharField(choices=[('video', 'Video'), ('literature', 'Text'), ('href', 'Text')], max_length=10),
        ),
    ]