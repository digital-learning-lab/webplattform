# Generated by Django 2.2.9 on 2020-01-13 14:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0002_auto_20190912_1730'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='newslettersubscrption',
            options={'verbose_name': 'Newsletter Subscription', 'verbose_name_plural': 'Newsletter Subscriptions'},
        ),
    ]