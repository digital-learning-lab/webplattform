# Generated by Django 3.2.15 on 2022-09-29 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0022_auto_20220929_1014'),
        ('user', '0005_auto_20200206_1049'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='emailchangerequest',
            options={'get_latest_by': 'modified'},
        ),
        migrations.AddField(
            model_name='dlluser',
            name='favorites',
            field=models.ManyToManyField(through='content.Favorite', to='content.Content'),
        ),
        migrations.AlterField(
            model_name='dlluser',
            name='json_data',
            field=models.JSONField(default=dict),
        ),
    ]