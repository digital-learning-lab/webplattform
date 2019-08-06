import logging
import os

from django.contrib.postgres.fields import IntegerRangeField, JSONField
from django.core.files import File
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField
from filer.models import Folder, Image
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel
from taggit.managers import TaggableManager

from .managers import ContentQuerySet
from dll.general.models import DllSlugField, PublisherModel
from dll.general.utils import get_default_tuhh_user, GERMAN_STATES
from dll.user.models import DllUser


logger = logging.getLogger('dll.content.models')


class Content(PublisherModel, PolymorphicModel):
    name = models.CharField(_("Titel des Tools/Trends/Unterrichtsbausteins"), max_length=200)
    slug = DllSlugField(populate_from='name')
    author = models.ForeignKey(DllUser, on_delete=models.SET(get_default_tuhh_user), verbose_name=_("Autor"))
    co_authors = models.ManyToManyField(DllUser, related_name='collaborative_content', verbose_name=_("Kollaborateure"))
    image = FilerImageField(on_delete=models.SET_NULL, null=True, verbose_name=_('Anzeigebild'))
    teaser = models.TextField(max_length=140, verbose_name=_("Teaser"), null=True, blank=True)
    learning_goals = models.TextField(_("Lernziele"), max_length=500, null=True, blank=True)
    related_content = models.ManyToManyField('self', verbose_name=_("Verwandte Tools/Trends/Unterrichtsbausteine"))
    view_count = models.PositiveIntegerField(default=0)
    base_folder = models.CharField(max_length=100, null=True)
    # additional_info: 'hinweise' for ubausteine, 'anmerkung'  for tools, 'hintergrund' for Trends
    additional_info = models.TextField(_("Hinweise/Anmerkungen/Hintergrund"), max_length=500, blank=True, null=True)
    competences = models.ManyToManyField('Competence', verbose_name=_("Kompetenzen"))
    sub_competences = models.ManyToManyField('SubCompetence', verbose_name=_("Subkompetenzen"))
    json_data = JSONField(default=dict)

    tags = TaggableManager()
    objects = PolymorphicManager.from_queryset(ContentQuerySet)()

    def __str__(self):
        return f"{self.name} ({self.__class__.__name__})"

    def suggest_related_content(self):
        """Suggested related content based on Solr results"""
        return self.objects.none()

    def update_or_add_image_from_path(self, path, update=False, image_name=None):
        if self.image:
            self.image.delete()
        filer_folder, created = Folder.objects.get_or_create(name=self.__class__.__name__)
        if image_name is None:
            image_name = str(os.path.dirname(path).split(os.sep)[-1]) + str(os.path.splitext(path))
        file = File(open(path, 'rb'), name=image_name)
        filer_image = Image.objects.create(original_filename=image_name,
                                           file=file,
                                           folder=filer_folder,
                                           owner=get_default_tuhh_user())
        self.image = filer_image
        self.save()

    class Meta:
        ordering = ['slug']


class TeachingModule(Content):
    description = models.TextField(_("Beschreibung"), null=True, blank=True)
    subject_of_tuition = models.TextField(_("Unterichtsgegenstand"), null=True, blank=True)
    educational_plan_reference = models.TextField(_("Bildungsplanbezug"), null=True, blank=True)
    school_class = IntegerRangeField(verbose_name=_("Jahrgangsstufe"), null=True, blank=True)
    estimated_time = models.CharField(max_length=250)
    equipment = models.TextField(_("Ausstattung"), max_length=500)
    state = models.CharField(_("Bundesland"), max_length=22, choices=GERMAN_STATES, null=True, blank=True)
    differentiating_attribute = models.TextField(_("Differenzierung"), max_length=500)
    expertise = models.TextField(_("Fachkompetenzen"), max_length=500, null=True, blank=True)
    subjects = models.ManyToManyField('Subject', verbose_name=_("Unterrichtsfach"))
    school_types = models.ManyToManyField('SchoolType', verbose_name=_("Schulform"))


class Tool(Content):
    STATUS_CHOICES = (
        ('on', _('Online')),
        ('off', _('Offline')),
        ('onoff', _('Online & Offline'))
    )

    USK_CHOICES = (
        ('usk0', _('Ohne Altersbeschränkung')),
        ('usk6', _('Ab 6 Jahren')),
        ('usk12', _('Ab 12 Jahren')),
        ('usk16', _('Ab 16 Jahren')),
        ('usk18', _('Ab 18 Jahren')),
    )

    PRIVACY_CHOICES = (
        (0, _("Unbekannt")),
        (1, _("Es werden keinerlei Daten erhoben")),
        (2, _("Personenbezogene Daten wie z.B. Logins werden geschützt auf dem Server abgelegt. "
              "Es greift die EU-Datenschutz-Grundverordnung.")),
        (3, _("Personenbezogene Daten werden erhoben. Dritte haben Zugriff auf diese Daten. "
              "Es greift die EU-Datenschutz-Grundverordnung.")),
        (4, _("Personenbezogene Daten werden erhoben. Es greift NICHT die EU-Datenschutz-Grundverordnung."))
    )

    operating_systems = models.ManyToManyField('OperatingSystem', verbose_name=_("Betriebssystem"))
    applications = models.ManyToManyField('ToolApplication', verbose_name=_("Anwendung"))
    status = models.CharField(_("Status"), max_length=7, choices=STATUS_CHOICES, default=None, null=True)
    requires_registration = models.BooleanField(null=True, blank=False)
    usk = models.CharField(_("Altersfreigabe"), max_length=5, choices=USK_CHOICES, null=True, blank=True)
    pro = models.CharField(_("Pro"), max_length=500, null=True, blank=True)
    contra = models.CharField(_("Kontra"), max_length=500, null=True, blank=True)
    privacy = models.IntegerField(_("Datenschutz"), choices=PRIVACY_CHOICES, null=True, blank=True)
    description = models.TextField(_("Beschreibung"), null=True, blank=True)
    usage = models.TextField(_("Nutzung"), null=True, blank=True)
    url = models.OneToOneField('ContentLink', on_delete=models.CASCADE, null=True)


class Trend(Content):
    LANGUAGE_CHOICHES = (
        ('german', _("Deutsch")),
        ('english', _("Englisch")),
        ('french', _("Französisch")),
        ('russian', _("Russisch")),
    )

    LICENCE_CHOICES = (
        (0, _("CC0")),
        (1, _("CC BY")),
        (2, _("CC BY 4.0")),
        (3, _("CC BY-NC")),
        (4, _("CC BY-NC-ND")),
        (5, _("CC BY-NC-SA")),
        (6, _("CC BY-ND")),
        (7, _("CC BY-SA")),
        (8, _("CC BY-SA 4.0")),
        (9, _("urheberrechtlich geschützt")),
    )

    CATEGORY_CHOICES = (
        (0, _("Keine Angaben")),
        (1, _("Forschung")),
        (2, _("Portal")),
        (3, _("Praxisbeispiel")),
        (4, _("Veröffentlichung")),
    )

    language = models.CharField(_("Sprache"), max_length=10, choices=LANGUAGE_CHOICHES, blank=True, null=True)
    licence = models.IntegerField(_("Lizenz"), choices=LICENCE_CHOICES, blank=True, null=True)
    category = models.IntegerField(_("Kategorie"), choices=CATEGORY_CHOICES, blank=True, null=True)
    target_group = models.CharField(_("Zielgruppe"), max_length=250, blank=True, null=True)
    publisher = models.CharField(_("Herausgeber"), max_length=250, blank=True, null=True)
    publisher_date = models.DateField(_("Datum der Veröffentlichung"), blank=True, null=True)
    central_contents = models.TextField(_("Zentrale Inhalte"), blank=True, null=True)
    url = models.URLField(_("Website"), blank=True, null=True)
    citation_info = models.CharField(_("Zitierhinweis"), max_length=500, blank=True, null=True)


class OperatingSystem(models.Model):
    """This is a class used to describe the availability of Tools for different the different operating systems"""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = _("Betriebssystem")
        verbose_name_plural = _("Betriebssysteme")


class Competence(TimeStampedModel):
    DEFAULT_NAMES = (
        (1, 'Suchen, Verarbeiten & Aufbewahren'),
        (2, 'Kommunizieren & Kooperieren'),
        (3, 'Produzieren & Präsentieren'),
        (4, 'Schützen & sicher Agieren'),
        (5, 'Problemlösen & Handeln'),
        (6, 'Analysieren & Reflektieren'),
    )

    DEFAULT_DESCRIPTIONS = {
        1: 'Zu dem Kompetenzbereich SUCHEN, VERARBEITEN & AUFBEWAHREN gehört der angemessene Umgang mit einer ständig '
           'wachsenden Menge an Daten und Informationen, die allen Menschen durch digitale Technologien zur Verfügung '
           'steht. Umgang meint dabei das Suchen, Finden und Auswählen relevanter und vertrauenswürdiger Quellen und '
           'Informationen, die kritische Reflexion und Bewertung dieser sowie die Organisation, Nutzung und '
           'Speicherung der gefundenen Daten und Informationen.',
        2: 'Um im digitalen Raum adäquat KOMMUNIZIEREN & KOOPERIEREN zu können, braucht es entsprechende Kompetenzen, '
           'digitale Werkzeuge zur angemessenen und effektiven Kommunikation einsetzen und in digitalen Umgebungen '
           'zielgerichtet kooperieren zu können. Dabei geht es vor allem darum, entsprechend der jeweiligen Situation '
           'und ausgerichtet an den Kommunikations- bzw. Kooperationspartnern die passenden Werkzeuge auszuwählen und '
           'entsprechende Umgangsregeln einzuhalten.',
        3: 'Mit digitalen Werkzeugen bieten sich vielfältige Möglichkeiten, eigene Inhalte zu PRODUZIEREN & '
           'PRÄSENTIEREN sowie bestehende Inhalte weiterzuverarbeiten. Dafür braucht es Kompetenzen, diese Werkzeuge '
           'sach- und adressatengerecht auszuwählen, Inhalte zu gestalten und zu veröffentlichen sowie mit den '
           'wesentlichen Rechtsgrundlagen vertraut zu sein.',
        4: 'Persönliche Daten, Privatsphäre und Persönlichkeitsrechte sind zentrale Themen, um sich selbst und andere '
           'im digitalen Raum zu SCHÜTZEN & SICHER zu AGIEREN. Dazu gehören auch Themen wie Cybermobbing und '
           '-kriminalität sowie Datenschutz und -sicherheit.',
        5: 'In dem Kompetenzbereich PROBLEMLÖSEN & HANDELN werden einerseits rein funktionale Fähigkeiten, wie der '
           'effektive Umgang mit Hardware und Software adressiert und andererseits Fähigkeiten beschrieben, diese '
           'digitalen Werkzeuge analysieren und für das eigene Handeln im digitalen Raum reflektieren und anwenden '
           'zu können.',
        6: 'Um an der digitalen Welt teilzuhaben und diese mit zu gestalten, sind das ANALYSIEREN & REFLEKTIEREN '
           'umso wichtiger. Dabei geht es darum, digitale Werkzeuge, Medien und Umgebungen zu verstehen, zu '
           'reflektieren und zu analysieren.'
    }

    cid = models.SmallIntegerField(unique=True, editable=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=600)

    def __str__(self):
        return dict(self.DEFAULT_NAMES)[int(self.cid)]

    def save(self, **kwargs):
        if self.pk is None:
            logger.debug('Created new Competence with ID {}'.format(self.cid))
            self.name = dict(self.DEFAULT_NAMES)[int(self.cid)]
            self.description = self.DEFAULT_DESCRIPTIONS[int(self.cid)]
        return super(Competence, self).save(**kwargs)

    class Meta:
        ordering = ["cid"]
        verbose_name = _("Kompetenz")
        verbose_name_plural = _("Kompetenzen")


class SubCompetence(TimeStampedModel):
    DEFAULT_NAMES = (
        (11, 'Suchen und Filtern'),
        (111, 'Arbeits- und Suchinteressen bestimmen'),
        (112, 'Passende Suchstrategien kennen, nutzen und weiterentwickeln'),
        (113, 'Verschiedene digitale Umgebungen entsprechend des Suchinteresses nutzen'),
        (114, 'Relevante und vertrauenswürdige Quellen und Informationen identifizieren und zusammenführen'),
        (12, 'Auswerten und Bewerten'),
        (121, 'Informationen und Daten analysieren, interpretieren und kritisch bewerten'),
        (122, 'Informationsquellen analysieren und kritisch bewerten'),
        (13, 'Speichern und Abrufen'),
        (131, 'Informationen und Daten sicher speichern, wiederfinden und von verschiedenen Orten abrufen'),
        (132, 'Informationen und Daten zusammenfassen, organisieren und strukturiert aufbewahren'),
        (21, 'Interagieren'),
        (211, 'Mit Hilfe unterschiedlicher digitaler Werkzeuge kommunizieren'),
        (212, 'Digitale Kommunikationsmöglichkeiten zielgerichtet- und situationsgerecht auswählen'),
        (22, 'Teilen'),
        (221, 'Dateien, Informationen und Links teilen'),
        (222, 'Referenzierungspraxis kennen und beherrschen (Quellenangaben)'),
        (23, 'Zusammenarbeiten'),
        (231,
         'Digitale Werkzeuge für die Zusammenarbeit bei der Zusammenführung von Informationen, Daten und Ressourcen nutzen'),
        (232, 'Digitale Werkzeuge bei der gemeinsamen Erarbeitung von Dokumenten nutzen'),
        (24, 'Umgangsregeln kennen und einhalten (Netiquette)'),
        (241, 'Verhaltensregeln bei digitaler Interaktion und Kooperation kennen und anwenden'),
        (242, 'Kommunikation der jeweiligen Umgebung anpassen'),
        (243,
         'Ethisch- moralische Prinzipien und Persönlichkeitsrechte bei der Kommunikation kennen, formulieren und einhalten'),
        (244, 'Kulturell-gesellschaftliche Normen in digitalen Umgebungen berücksichtigen'),
        (25, 'An der Gesellschaft aktiv teilhaben'),
        (251, 'Öffentliche und private Dienste kennen, reflektieren und angemessen anwenden'),
        (252, 'Medienerfahrungen reflektieren, weitergeben und in kommunikative Prozesse einbringen'),
        (253, 'Als selbstbestimmter Bürger aktiv an der Gesellschaft teilhaben'),
        (31, 'Entwickeln und Produzieren'),
        (311, 'Mehrere technische Bearbeitungswerkzeuge kennen und anwenden'),
        (312,
         'Eigene Medienprodukte planen und in verschiedenen Formaten gestalten, präsentieren, veröffentlichen und teilen'),
        (32, 'Weiterverarbeiten und Integrieren'),
        (321, 'Inhalte in verschiedenen Formaten bearbeiten, zusammenführen, präsentieren, veröffentlichen und teilen'),
        (322,
         'Informationen, Inhalte und vorhandene digitale Produkte weiterverarbeiten und in bestehendes Wissen integrieren'),
        (33, 'Rechtliche Vorgaben beachten'),
        (331, 'Bedeutung von Urheberrecht und geistigem Eigentum kennen'),
        (332, 'Urheber- und Nutzungsrechte (Lizenzen) bei eigenen und fremden Werken überprüfen und beachten'),
        (333, 'Persönlichkeitsrechte (u.a. des Bildrechts) beachten'),
        (41, 'Sicher in digitalen Umgebungen agieren'),
        (411, 'Risiken und Gefahren in digitalen Umgebungen kennen, reflektieren und berücksichtigen'),
        (412, 'Strategien zum Schutz (gegen z.B. Cyberkriminalität) entwickeln und anwenden'),
        (42, 'Persönliche Daten und Privatsphäre schützen'),
        (421, 'Maßnahmen für Datensicherheit und gegen Datenmissbrauch kennen und beachten'),
        (422, 'Privatsphäre in digitalen Umgebungen durch geeignete Maßnahmen schützen'),
        (423, 'Sicherheitseinstellungen ständig aktualisieren'),
        (424, 'Jugendschutz- und Verbraucherschutzmaßnahmen berücksichtigen'),
        (43, 'Gesundheit schützen'),
        (431, 'Suchtgefahren vermeiden, sich Selbst und andere vor möglichen Gefahren schützen'),
        (432, 'Digitale Technologien gesundheitsbewusst nutzen'),
        (433, 'Digitale Technologien für soziales Wohlergehen und Eingliederung nutzen'),
        (44, 'Natur und Umwelt schützen'),
        (441, 'Umweltauswirkungen digitaler Technologien berücksichtigen'),
        (51, 'Technische Probleme lösen'),
        (511, 'Anforderungen an digitale Umgebungen formulieren'),
        (512, 'Technische Probleme identifizieren'),
        (513, 'Bedarfe für Lösungen ermitteln und Lösungen finden bzw. Lösungsstrategien entwickeln'),
        (52, 'Werkzeuge bedarfsgerecht einsetzen'),
        (521, 'Eine Vielzahl von digitalen Werkzeugen kennen und kreativ anwenden'),
        (522, 'Anforderungen an digitale Werkzeuge formulieren'),
        (523, 'Passende Werkzeuge zur Lösung identifizieren'),
        (524, 'Digitale Umgebungen und Werkzeuge zum persönlichen Gebrauch anpassen'),
        (53, 'Eigene Defizite ermitteln und nach Lösungen suchen'),
        (531, 'Eigene Defizite bei der Nutzung digitaler Werkzeuge erkennen und Strategien zur Beseitigung entwickeln'),
        (532, 'Eigene Strategien zur Problemlösung mit anderen teilen'),
        (54, 'Digitale  Werkzeuge und  Medien zum Lernen, Arbeiten und  Problemlösen nutzen'),
        (541, 'Effektive digitale Lernmöglichkeiten finden, bewerten und nutzen'),
        (542, 'Persönliches System von vernetzten digitalen Lernressourcen selbst organisieren'),
        (55, 'Funktionsweisen erkennen und formulieren'),
        (551, 'Funktionsweisen und grundlegende Prinzipien der digitalen Welt kennen, verstehen und bewusst nutzen'),
        (552, 'Algorithmische Strukturen in genutzten digitalen Tools erkennen, verstehen und formulieren'),
        (553,
         'Eine strukturierte, algorithmische oder automatisierte Sequenz zur Lösung eines Problems planen, verwenden und umsetzen'),
        (61, 'Medien analysieren und bewerten'),
        (611, 'Gestaltungsmittel von digitalen Medienangeboten kennen und bewerten'),
        (612,
         'Interessengeleitete Setzung, Verbreitung und Dominanz von Themen in digitalen Umgebungen erkennen und beurteilen'),
        (613,
         'Wirkungen von Medien in der digitalen Welt (z. B. mediale Konstrukte, Stars, Idole, Computerspiele, mediale Gewaltdarstellungen) analysieren und konstruktiv damit umgehen'),
        (62, 'Medien in der digitalen Welt verstehen und reflektieren'),
        (621, 'Vielfalt der digitalen Medienlandschaft kennen'),
        (622,
         'Chancen und Risiken des Mediengebrauchs in unterschiedlichen Lebensbereichen erkennen, eigenen Mediengebrauch reflektieren und ggf. modifizieren'),
        (623, 'Vorteile und Risiken von Geschäftsaktivitäten und Services im Internet analysieren und beurteilen'),
        (624,
         'Wirtschaftliche Bedeutung der digitalen Medien und digitaler Technologien kennen und sie für eigene Geschäftsideen nutzen'),
        (625,
         'Die Bedeutung von digitalen Medien für die politische Meinungsbildung und Entscheidungsfindung kennen und nutzen'),
        (626,
         'Potenziale der Digitalisierung im Sinne sozialer Integration und sozialer Teilhabe erkennen, analysieren und reflektieren'),
    )

    cid = models.SmallIntegerField(unique=True, editable=False)
    name = models.CharField(max_length=500)
    competence = models.ForeignKey('Competence', on_delete=models.CASCADE)

    def save(self, **kwargs):
        if self.pk is None:
            logger.debug('Created new SubCompetence with ID {}'.format(self.cid))
            self.name = dict(self.DEFAULT_NAMES)[int(self.cid)]
            competence, created = Competence.objects.get_or_create(cid=str(self.cid)[0])
            self.competence = competence
        return super(SubCompetence, self).save(**kwargs)

    def __str__(self):
        return dict(self.DEFAULT_NAMES)[int(self.cid)]

    class Meta:
        ordering = ["cid"]
        verbose_name = _("Subkompetenz")
        verbose_name_plural = _("Subkompetenzen")


class ContentLink(TimeStampedModel):
    TYPE_CHOICES = (
        ('audio', _('Audio')),
        ('video', _('Video')),
        ('href', _('Webseite')),
        ('literature', _('Literatur')),
    )

    url = models.URLField(max_length=2083)
    name = models.CharField(max_length=300)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    content = models.ForeignKey(
        'Content',
        on_delete=models.CASCADE,
        null=True  # null=True because can be a one2one relation to e.g. Tool
    )


class ContentFile(TimeStampedModel):
    file = FilerFileField(on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.ForeignKey('Content', on_delete=models.CASCADE)


class Subject(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = _("Unterrichtsfach")
        verbose_name_plural = _("Unterrichtsfächer")


class SchoolType(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = _("Schulform")
        verbose_name_plural = _("Schulformen")


class ToolApplication(TimeStampedModel):
    CHOICES = (
        ('App', _("App")),
        ('Website', _("Website")),
        ('Programm', _("Programm")),
        ('Browser-Add-on', _("Browser-Add-on"))
    )

    name = models.CharField(max_length=50, choices=CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = _("Anwendung")
        verbose_name_plural = _("Anwendungen")


@receiver(models.signals.post_delete, sender=Content)
def auto_delete_filer_image_on_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete()
