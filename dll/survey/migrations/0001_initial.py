# Generated by Django 2.2.17 on 2020-11-30 16:25

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Survey",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Title")),
                (
                    "description",
                    ckeditor.fields.RichTextField(verbose_name="Description"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SurveyQuestion",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "question_type",
                    models.SmallIntegerField(
                        choices=[
                            (0, "Radio"),
                            (1, "Dropdown"),
                            (2, "Checkbox"),
                            (3, "Text"),
                        ],
                        verbose_name="Type",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Title")),
                (
                    "required",
                    models.BooleanField(default=False, verbose_name="Required"),
                ),
                (
                    "survey",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="survey.Survey"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Trigger",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "event",
                    models.CharField(
                        choices=[
                            ("pageOpen", "Open Page"),
                            ("leaveIntent", "Leave Intent"),
                            ("submitContent", "Content Submission"),
                        ],
                        max_length=64,
                        verbose_name="Trigger Type",
                    ),
                ),
                (
                    "delay",
                    models.PositiveIntegerField(default=1000, verbose_name="Delay"),
                ),
                (
                    "url",
                    models.URLField(blank=True, null=True, verbose_name="Page Url"),
                ),
                (
                    "survey",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="survey.Survey"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SurveyResultAnswer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.TextField(verbose_name="Value")),
                (
                    "question",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="survey.SurveyQuestion",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SurveyResult",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "survey",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="survey.Survey"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SurveyQuestionChoice",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("label", models.CharField(max_length=64, verbose_name="Label")),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="survey.SurveyQuestion",
                    ),
                ),
            ],
        ),
    ]
