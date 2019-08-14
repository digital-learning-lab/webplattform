import logging
import os

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import IntegerRangeField, JSONField, ArrayField
from django.core.files import File
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from filer.fields.file import FilerFileField
from filer.fields.image import FilerImageField
from filer.models import Folder, Image
from guardian.shortcuts import assign_perm, remove_perm
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel
from taggit.managers import TaggableManager

from .managers import ContentQuerySet
from dll.general.models import DllSlugField, PublisherModel
from dll.user.utils import get_default_tuhh_user, get_bsb_reviewer_group, get_tuhh_reviewer_group
from dll.general.utils import GERMAN_STATES
from dll.user.models import DllUser


logger = logging.getLogger('dll.content.models')


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


class Content(PublisherModel, PolymorphicModel):
    name = models.CharField(_("Titel des Tools/Trends/Unterrichtsbausteins"), max_length=200)
    slug = DllSlugField(populate_from='name')
    author = models.ForeignKey(DllUser, on_delete=models.SET(get_default_tuhh_user), verbose_name=_("Autor"))
    co_authors = models.ManyToManyField(DllUser, related_name='collaborative_content', verbose_name=_("Kollaborateure"))
    image = FilerImageField(on_delete=models.SET_NULL, null=True, verbose_name=_('Anzeigebild'))
    teaser = models.TextField(max_length=140, verbose_name=_("Teaser"), null=True, blank=True)
    learning_goals = ArrayField(models.CharField(max_length=200), verbose_name=_("Lernziele"), default=list)
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
        if self.is_public:
            return f"{self.name} ({self.__class__.__name__}, public)"
        else:
            return f"{self.name} ({self.__class__.__name__})"

    @property
    def review(self):
        try:
            return self.reviews.get(is_active=True)
        except Review.DoesNotExist:
            return None
        except Review.MultipleObjectsReturned:
            logger.error("Multiple active reviews returned for Content with pk {}. "
                         "Setting the latest one as active".format(self.pk))
            review_pks = self.reviews.filter(is_active=True).order_by('-modified').values_list('pk', flat=True)
            active_review = Review.objects.get(pk=review_pks[0])
            Review.objects.filter(pk__in=review_pks[1:]).update(is_active=False)
            return active_review

    def submit_for_review(self):
        if self.review:
            # content was declined and now resubmitted
            review = self.review
            review.status = Review.IN_PROGRESS
            review.save()
        else:
            Review.objects.create(content=self, is_active=True)

    def copy_relations(self, src, dst):
        # image
        super(Content, self).copy_relations(src, dst)
        dst_image = src.image
        dst_image.pk = None
        dst_image.id = None
        file_name, extension = os.path.splitext(dst_image.label)
        file_name += " (public)"
        dst_image.name = file_name + extension
        dst_image.save()
        dst.image = dst_image
        dst.save()

        # co-authors
        dst.co_authors.add(*src.co_authors.all())

        # related content
        dst.related_content.add(*src.related_content.all())

        # competences
        dst.competences.add(*src.competences.all())
        dst.sub_competences.add(*src.sub_competences.all())

        # tags
        dst.tags.add(*src.tags.all())

        # links and files
        for link in src.contentlink_set.all():
            link.pk, link.id, link.created, link.modified = None, None, None, None
            link.content = dst
            link.save()

        for file in src.contentfile_set.all():
            file.pk, file.id, file.created, file.modified = None, None, None, None
            file.content = dst
            file.save()

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

    @cached_property
    def content_files(self):
        return self.contentfile_set.all()

    @cached_property
    def video_links(self):
        return self.contentlink_set.filter(type='video')

    @cached_property
    def textual_links(self):
        return self.contentlink_set.filter(Q(type='href') | Q(type='literature'))

    @cached_property
    def has_tutorial_links(self):
        return bool(self.textual_links.count() + self.video_links.count())

    @cached_property
    def related_teaching_modules(self):
        return TeachingModule.objects.filter(related_content__in=[self.pk])

    @cached_property
    def related_tools(self):
        return Tool.objects.filter(related_content__in=[self.pk])

    @cached_property
    def related_trends(self):
        return Trend.objects.filter(related_content__in=[self.pk])

    class Meta:
        ordering = ['slug']


class TeachingModule(Content):
    description = models.TextField(_("Beschreibung"), null=True, blank=True)
    subject_of_tuition = ArrayField(models.CharField(max_length=200), verbose_name=_("Unterichtsgegenstand"),
                                    default=list)
    educational_plan_reference = models.TextField(_("Bildungsplanbezug"), null=True, blank=True)
    school_class = IntegerRangeField(verbose_name=_("Jahrgangsstufe"), null=True, blank=True)
    # estimated time e.g. Doppelstunde,unterrichtsbegleitend
    estimated_time = ArrayField(models.CharField(max_length=200), verbose_name=_("Zeitumfang"), default=list)
    equipment = ArrayField(models.CharField(max_length=200), verbose_name=_("Ausstattung"), default=list)
    state = models.CharField(_("Bundesland"), max_length=22, choices=GERMAN_STATES, null=True, blank=True)
    differentiating_attribute = models.TextField(_("Differenzierung"), max_length=500)
    expertise = ArrayField(models.CharField(max_length=200), verbose_name=_("Fachkompetenzen"), default=list)
    subjects = models.ManyToManyField('Subject', verbose_name=_("Unterrichtsfach"))
    school_types = models.ManyToManyField('SchoolType', verbose_name=_("Schulform"))
    licence = models.IntegerField(_("Lizenz"), choices=LICENCE_CHOICES, blank=True, null=True)

    class Meta:
        permissions = (
            ('review_teachingmodule', _("Can review Teaching Module")),
        )

    @property
    def type(self):
        return 'teaching-module'

    @property
    def type_verbose(self):
        return 'Unterrichtsbaustein'

    def copy_relations(self, src, dst):
        super(TeachingModule, self).copy_relations(src, dst)
        dst.subjects.add(*src.subjects.all())
        dst.school_types.add(*src.school_types.all())

    def get_absolute_url(self):
        return reverse('teaching-module-detail', kwargs={'slug': self.slug})


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
    pro = ArrayField(models.CharField(max_length=200), verbose_name=_("Pro"), default=list)
    contra = ArrayField(models.CharField(max_length=200), verbose_name=_("Kontra"), default=list)
    privacy = models.IntegerField(_("Datenschutz"), choices=PRIVACY_CHOICES, null=True, blank=True)
    description = models.TextField(_("Beschreibung"), null=True, blank=True)
    usage = models.TextField(_("Nutzung"), null=True, blank=True)
    url = models.OneToOneField('ContentLink', on_delete=models.CASCADE, null=True)

    class Meta:
        permissions = (
            ('review_tool', _("Can review Tool")),
        )

    @property
    def type_verbose(self):
        return 'Tool'

    @property
    def type(self):
        return 'tool'

    def get_absolute_url(self):
        return reverse('tool-detail', kwargs={'slug': self.slug})

    def copy_relations(self, src, dst):
        super(Tool, self).copy_relations(src, dst)
        dst.operating_systems.add(*src.operating_systems.all())
        dst.applications.add(*src.applications.all())

        url_clone = src.url
        url_clone.pk = None
        url_clone.id = None
        url_clone.created = None
        url_clone.modified = None
        url_clone.save()
        dst.url = url_clone
        dst.save()


class Trend(Content):
    LANGUAGE_CHOICHES = (
        ('german', _("Deutsch")),
        ('english', _("Englisch")),
        ('french', _("Französisch")),
        ('russian', _("Russisch")),
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
    target_group = ArrayField(models.CharField(max_length=200), verbose_name=_("Zielgruppe"), default=list)
    publisher = ArrayField(models.CharField(max_length=200), verbose_name=_("Herausgeber"), default=list)
    publisher_date = models.DateField(_("Datum der Veröffentlichung"), blank=True, null=True)
    central_contents = models.TextField(_("Zentrale Inhalte"), blank=True, null=True)
    citation_info = models.CharField(_("Zitierhinweis"), max_length=500, blank=True, null=True)

    @property
    def type(self):
        return 'trend'

    @property
    def type_verbose(self):
        return 'Trend'

    def get_absolute_url(self):
        return reverse('trend-detail', kwargs={'slug': self.slug})

    def copy_relations(self, src, dst):
        super(Trend, self).copy_relations(src, dst)

    class Meta:
        permissions = (
            ('review_trend', _("Can review Trend")),
        )


class Review(TimeStampedModel):
    NEW, IN_PROGRESS, ACCEPTED, DECLINED = 0, 1, 2, 3
    STATUS_CHOICES = (
        (NEW, _("Neu")),
        (IN_PROGRESS, _("In Bearbeitung")),
        (ACCEPTED, _("Akzeptiert")),
        (DECLINED, _("Abgelehnt")),
    )
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='reviews')
    json_data = JSONField(default=dict)
    is_active = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=NEW)

    def accept(self):
        self.status = self.ACCEPTED
        self.is_active = False
        self.save()
        self.content.publish()

    def decline(self):
        self.status = self.DECLINED
        self.save()


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
    slug = DllSlugField(
        max_length=512,
        populate_from='name'
    )

    @property
    def icon_class(self):
        """used for mapping to css icons"""
        return "icon-competence-id-{}".format(self.cid)

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
    slug = DllSlugField(
        max_length=512,
        populate_from='name'
    )

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


class TrendLink(TimeStampedModel):
    url = models.URLField(max_length=2083)
    name = models.CharField(max_length=300)
    trend = models.ForeignKey('Trend', on_delete=models.CASCADE)


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
    # for reasons unknown, this works without specifying the concrete sender model
    if instance.image:
        instance.image.delete()


def assign_author_permissions(sender, instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(instance)
        codenames = [x + content_type.model for x in ('add_', 'view_', 'change_', 'delete_')]
        for codename in codenames:
            permission = Permission.objects.get(
                content_type=content_type,
                codename=codename
            )
            assign_perm(permission, instance.author, instance)


for subclass in Content.__subclasses__():
    models.signals.post_save.connect(assign_author_permissions, sender=subclass)


@receiver(models.signals.m2m_changed, sender=Content.co_authors.through)
def update_co_authors_permissions(sender, instance, **kwargs):
    action = kwargs['action']
    content_type = ContentType.objects.get_for_model(instance)
    codename = 'change_' + content_type.model
    permission = Permission.objects.get(
        content_type=content_type,
        codename=codename
    )
    if kwargs['pk_set']:
        if action == 'post_add':
            users = DllUser.objects.filter(pk__in=kwargs['pk_set'])
            for user in users:
                assign_perm(permission, user, instance)
        elif action == 'post_remove':
            users = DllUser.objects.filter(pk__in=kwargs['pk_set'])
            for user in users:
                remove_perm(permission, user, instance)


@receiver(models.signals.post_save, sender=Review)
def toggle_permissions_based_on_review_status(sender, instance: Review, **kwargs):
    content_type = ContentType.objects.get_for_model(instance.content)
    codename = 'change_' + content_type.model
    change_permission = Permission.objects.get(
        content_type=content_type,
        codename=codename
    )
    change_review_permission = Permission.objects.get(
        content_type=ContentType.objects.get_for_model(instance),
        codename='change_review'
    )

    if instance.status in [Review.NEW, Review.IN_PROGRESS]:
        remove_perm(change_permission, instance.content.author, instance.content)
        for co_author in instance.content.co_authors.all():
            remove_perm(change_permission, co_author, instance.content)
        if isinstance(instance.content, TeachingModule):
            group = get_bsb_reviewer_group()
            assign_perm(change_review_permission, group, instance)
        elif isinstance(instance.content, Tool) or isinstance(instance.content, Trend):
            group = get_tuhh_reviewer_group()
            assign_perm(change_review_permission, group, instance)

    elif instance.status in [Review.ACCEPTED, Review.DECLINED]:
        assign_perm(change_permission, instance.content.author, instance.content)
        for co_author in instance.content.co_authors.all():
            assign_perm(change_permission, co_author, instance.content)
        if isinstance(instance.content, TeachingModule):
            group = get_bsb_reviewer_group()
            remove_perm(change_review_permission, group, instance)
        elif isinstance(instance.content, Tool) or isinstance(instance.content, Trend):
            group = get_tuhh_reviewer_group()
            remove_perm(change_review_permission, group, instance)
