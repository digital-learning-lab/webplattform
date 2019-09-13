# Generated by Django 2.2.4 on 2019-09-12 15:30

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
import django.contrib.postgres.fields.ranges
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import dll.general.models
import dll.user.utils
import filer.fields.file
import filer.fields.image
import meta.models
import rules.contrib.models
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sites', '0002_alter_domain_unique'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.FILER_IMAGE_MODEL),
        ('filer', '0011_auto_20190418_0137'),
        ('taggit', '0003_taggeditem_add_unique_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('cid', models.SmallIntegerField(editable=False, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=600)),
                ('slug', dll.general.models.DllSlugField(blank=True, editable=False, max_length=512, populate_from='name')),
            ],
            options={
                'verbose_name': 'Kompetenz',
                'verbose_name_plural': 'Kompetenzen',
                'ordering': ['cid'],
            },
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('publisher_is_draft', models.BooleanField(db_index=True, default=True, editable=False)),
                ('name', models.CharField(max_length=200, verbose_name='Titel des Tools/Trends/Unterrichtsbausteins')),
                ('slug', dll.general.models.DllSlugField(allow_duplicates=True, blank=True, editable=False, overwrite=True, populate_from='name')),
                ('teaser', models.TextField(blank=True, max_length=140, null=True, verbose_name='Teaser')),
                ('learning_goals', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, null=True, size=None, verbose_name='Lernziele')),
                ('view_count', models.PositiveIntegerField(default=0, editable=False)),
                ('base_folder', models.CharField(editable=False, max_length=100, null=True)),
                ('additional_info', models.TextField(blank=True, max_length=1500, null=True, verbose_name='Hinweise/Anmerkungen/Hintergrund')),
                ('json_data', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('ex_authors', models.CharField(blank=True, max_length=800, null=True, verbose_name='Ex-Autoren')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Autor')),
                ('co_authors', models.ManyToManyField(blank=True, related_name='collaborative_content', to=settings.AUTH_USER_MODEL, verbose_name='Kollaborateure')),
                ('competences', models.ManyToManyField(blank=True, to='content.Competence', verbose_name='Kompetenzen')),
                ('image', filer.fields.image.FilerImageField(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.FILER_IMAGE_MODEL, verbose_name='Anzeigebild')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_content.content_set+', to='contenttypes.ContentType')),
                ('publisher_linked', models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='publisher_draft', to='content.Content')),
                ('related_content', models.ManyToManyField(blank=True, related_name='_content_related_content_+', to='content.Content', verbose_name='Verwandte Tools/Trends/Unterrichtsbausteine')),
                ('site', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='sites.Site')),
            ],
            options={
                'verbose_name': 'Inhalt',
                'verbose_name_plural': 'Inhalte',
                'ordering': ['slug'],
                'permissions': (('can_publish', 'Can publish'),),
                'abstract': False,
            },
            bases=(meta.models.ModelMeta, rules.contrib.models.RulesModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='HelpText',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('content_type', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='help_text', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OperatingSystem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Betriebssystem',
                'verbose_name_plural': 'Betriebssysteme',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SchoolType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Schulform',
                'verbose_name_plural': 'Schulformen',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Unterrichtsfach',
                'verbose_name_plural': 'Unterrichtsfächer',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ToolApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(choices=[('App', 'App'), ('Website', 'Website'), ('Programm', 'Programm'), ('Browser-Add-on', 'Browser-Add-on')], max_length=50)),
            ],
            options={
                'verbose_name': 'Anwendung',
                'verbose_name_plural': 'Anwendungen',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tool',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='content.Content')),
                ('status', models.CharField(choices=[('on', 'Online'), ('off', 'Offline'), ('onoff', 'Online & Offline')], default=None, max_length=7, null=True, verbose_name='Status')),
                ('requires_registration', models.BooleanField(null=True)),
                ('usk', models.CharField(blank=True, choices=[('usk0', 'Ohne Altersbeschränkung'), ('usk6', 'Ab 6 Jahren'), ('usk12', 'Ab 12 Jahren'), ('usk16', 'Ab 16 Jahren'), ('usk18', 'Ab 18 Jahren')], max_length=5, null=True, verbose_name='Altersfreigabe')),
                ('pro', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, null=True, size=None, verbose_name='Pro')),
                ('contra', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, null=True, size=None, verbose_name='Kontra')),
                ('privacy', models.IntegerField(blank=True, choices=[(0, 'Unbekannt'), (1, 'Es werden keinerlei Daten erhoben'), (2, 'Personenbezogene Daten wie z.B. Logins werden geschützt auf dem Server abgelegt. Es greift die EU-Datenschutz-Grundverordnung.'), (3, 'Personenbezogene Daten werden erhoben. Dritte haben Zugriff auf diese Daten. Es greift die EU-Datenschutz-Grundverordnung.'), (4, 'Personenbezogene Daten werden erhoben. Es greift NICHT die EU-Datenschutz-Grundverordnung.')], null=True, verbose_name='Datenschutz')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Beschreibung')),
                ('usage', models.TextField(blank=True, null=True, verbose_name='Nutzung')),
                ('applications', models.ManyToManyField(blank=True, to='content.ToolApplication', verbose_name='Anwendung')),
                ('operating_systems', models.ManyToManyField(blank=True, to='content.OperatingSystem', verbose_name='Betriebssystem')),
            ],
            options={
                'verbose_name': 'Tool',
                'verbose_name_plural': 'Tools',
                'permissions': (('can_publish', 'Can publish'),),
                'abstract': False,
            },
            bases=('content.content',),
        ),
        migrations.CreateModel(
            name='Trend',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='content.Content')),
                ('language', models.CharField(blank=True, choices=[('german', 'Deutsch'), ('english', 'Englisch')], max_length=10, null=True, verbose_name='Sprache')),
                ('licence', models.IntegerField(blank=True, choices=[(0, 'CC0'), (1, 'CC BY'), (2, 'CC BY 4.0'), (3, 'CC BY-NC'), (4, 'CC BY-NC-ND'), (5, 'CC BY-NC-SA'), (6, 'CC BY-ND'), (7, 'CC BY-SA'), (8, 'CC BY-SA 4.0'), (9, 'urheberrechtlich geschützt')], null=True, verbose_name='Lizenz')),
                ('category', models.IntegerField(blank=True, choices=[(0, 'Keine Angaben'), (1, 'Forschung'), (2, 'Portal'), (3, 'Praxisbeispiel'), (4, 'Veröffentlichung')], null=True, verbose_name='Kategorie')),
                ('target_group', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, null=True, size=None, verbose_name='Zielgruppe')),
                ('publisher', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, null=True, size=None, verbose_name='Herausgeber')),
                ('publisher_date', models.DateField(blank=True, null=True, verbose_name='Datum der Veröffentlichung')),
                ('central_contents', models.TextField(blank=True, null=True, verbose_name='Zentrale Inhalte')),
                ('citation_info', models.CharField(blank=True, max_length=500, null=True, verbose_name='Zitierhinweis')),
            ],
            options={
                'verbose_name': 'Trend',
                'verbose_name_plural': 'Trends',
                'permissions': (('can_publish', 'Can publish'),),
                'abstract': False,
            },
            bases=('content.content',),
        ),
        migrations.CreateModel(
            name='SubCompetence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('cid', models.SmallIntegerField(editable=False, unique=True)),
                ('name', models.CharField(max_length=500)),
                ('ordering', models.IntegerField(unique=True)),
                ('slug', dll.general.models.DllSlugField(blank=True, editable=False, max_length=512, populate_from='name')),
                ('competence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='content.Competence')),
            ],
            options={
                'verbose_name': 'Subkompetenz',
                'verbose_name_plural': 'Subkompetenzen',
                'ordering': ['cid'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('json_data', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('is_active', models.BooleanField(default=False)),
                ('status', models.IntegerField(choices=[(0, 'Neu'), (1, 'In Bearbeitung'), (2, 'Akzeptiert'), (3, 'Abgelehnt')], default=0)),
                ('count', models.PositiveSmallIntegerField(default=0)),
                ('accepted_by', models.ForeignKey(null=True, on_delete=models.SET(dll.user.utils.get_default_tuhh_user), related_name='accepted_reviews', to=settings.AUTH_USER_MODEL)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='content.Content')),
                ('declined_by', models.ForeignKey(null=True, on_delete=models.SET(dll.user.utils.get_default_tuhh_user), related_name='declined_reviews', to=settings.AUTH_USER_MODEL)),
                ('submitted_by', models.ForeignKey(null=True, on_delete=models.SET(dll.user.utils.get_default_tuhh_user), related_name='submitted_reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContentLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('url', models.URLField(max_length=2083)),
                ('name', models.CharField(max_length=300)),
                ('type', models.CharField(choices=[('audio', 'Audio'), ('video', 'Video'), ('href', 'Webseite'), ('literature', 'Literatur')], max_length=10)),
                ('content', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='content.Content')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContentFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('title', models.CharField(max_length=100)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='content.Content')),
                ('file', filer.fields.file.FilerFileField(on_delete=django.db.models.deletion.CASCADE, to='filer.File')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='content',
            name='sub_competences',
            field=models.ManyToManyField(blank=True, to='content.SubCompetence', verbose_name='Subkompetenzen'),
        ),
        migrations.AddField(
            model_name='content',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.CreateModel(
            name='TrendLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('url', models.URLField(max_length=2083)),
                ('name', models.CharField(max_length=300)),
                ('trend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='content.Trend')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ToolLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('url', models.URLField(blank=True, max_length=2083, null=True)),
                ('name', models.CharField(blank=True, max_length=300, null=True)),
                ('tool', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='url', to='content.Tool')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TeachingModule',
            fields=[
                ('content_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='content.Content')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Beschreibung')),
                ('subject_of_tuition', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, null=True, size=None, verbose_name='Unterichtsgegenstand')),
                ('educational_plan_reference', models.TextField(blank=True, null=True, verbose_name='Bildungsplanbezug')),
                ('school_class', django.contrib.postgres.fields.ranges.IntegerRangeField(blank=True, null=True, verbose_name='Jahrgangsstufe')),
                ('estimated_time', models.CharField(blank=True, max_length=200, null=True, verbose_name='Zeitumfang')),
                ('equipment', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, null=True, size=None, verbose_name='Ausstattung')),
                ('state', models.CharField(blank=True, choices=[('nordrhein-westfalen', 'Nordrhein-Westfalen'), ('niedersachsen', 'Niedersachsen'), ('bayern', 'Bayern'), ('rheinland-pfalz', 'Rheinland-Pfalz'), ('hessen', 'Hessen'), ('saarland', 'Saarland'), ('berlin', 'Berlin'), ('brandenburg', 'Brandenburg'), ('schleswig-holstein', 'Schleswig-Holstein'), ('mecklenburg-vorpommern', 'Mecklenburg-Vorpommern'), ('thueringen', 'Thüringen'), ('sachsen', 'Sachsen'), ('sachsen-anhalt', 'Sachsen-Anhalt'), ('bremen', 'Bremen'), ('baden-wuerttemberg', 'Baden-Württemberg'), ('hamburg', 'Hamburg')], max_length=22, null=True, verbose_name='Bundesland')),
                ('differentiating_attribute', models.TextField(blank=True, max_length=700, null=True, verbose_name='Differenzierung')),
                ('expertise', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, null=True, size=None, verbose_name='Fachkompetenzen')),
                ('licence', models.IntegerField(blank=True, choices=[(0, 'CC0'), (1, 'CC BY'), (2, 'CC BY 4.0'), (3, 'CC BY-NC'), (4, 'CC BY-NC-ND'), (5, 'CC BY-NC-SA'), (6, 'CC BY-ND'), (7, 'CC BY-SA'), (8, 'CC BY-SA 4.0'), (9, 'urheberrechtlich geschützt')], null=True, verbose_name='Lizenz')),
                ('school_types', models.ManyToManyField(blank=True, to='content.SchoolType', verbose_name='Schulform')),
                ('subjects', models.ManyToManyField(blank=True, to='content.Subject', verbose_name='Unterrichtsfach')),
            ],
            options={
                'verbose_name': 'Unterrichtsbaustein',
                'verbose_name_plural': 'Unterrichtsbausteine',
                'permissions': (('can_publish', 'Can publish'),),
                'abstract': False,
            },
            bases=('content.content',),
        ),
        migrations.CreateModel(
            name='HelpTextField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=100)),
                ('text', models.TextField()),
                ('help_text', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='help_text_fields', to='content.HelpText')),
            ],
            options={
                'unique_together': {('name', 'help_text')},
            },
        ),
    ]
