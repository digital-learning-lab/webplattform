import logging
import os

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import IntegerRangeField, JSONField, ArrayField
from django.contrib.sites.models import Site
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
from filer.models import Folder, Image, File as FilerFile
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel
from rules.contrib.models import RulesModelMixin, RulesModelBaseMixin
from taggit.managers import TaggableManager

from .managers import ContentQuerySet
from dll.general.models import DllSlugField, PublisherModel
from dll.user.utils import get_default_tuhh_user, get_bsb_reviewer_group, get_tuhh_reviewer_group
from dll.general.utils import GERMAN_STATES, custom_slugify
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


class Content(RulesModelMixin, PublisherModel, PolymorphicModel):
    name = models.CharField(_("Titel des Tools/Trends/Unterrichtsbausteins"), max_length=200)
    slug = DllSlugField(populate_from='name', overwrite=True, allow_duplicates=True)
    # todo check if xxx-2 slugs are created if name does not change
    author = models.ForeignKey(DllUser, on_delete=models.SET(get_default_tuhh_user), verbose_name=_("Autor"))
    co_authors = models.ManyToManyField(DllUser, related_name='collaborative_content',
                                        verbose_name=_("Kollaborateure"), blank=True)
    image = FilerImageField(on_delete=models.SET_NULL, null=True, verbose_name=_('Anzeigebild'))
    teaser = models.TextField(max_length=140, verbose_name=_("Teaser"), null=True, blank=True)
    learning_goals = ArrayField(models.CharField(max_length=200), verbose_name=_("Lernziele"), default=list, null=True,
                                blank=True)
    related_content = models.ManyToManyField('self', verbose_name=_("Verwandte Tools/Trends/Unterrichtsbausteine"),
                                             blank=True)
    view_count = models.PositiveIntegerField(default=0, editable=False)
    base_folder = models.CharField(max_length=100, null=True, editable=False)
    # additional_info: 'hinweise' for ubausteine, 'anmerkung'  for tools, 'hintergrund' for Trends
    additional_info = models.TextField(_("Hinweise/Anmerkungen/Hintergrund"), max_length=500, blank=True, null=True)
    competences = models.ManyToManyField('Competence', verbose_name=_("Kompetenzen"), blank=True)
    sub_competences = models.ManyToManyField('SubCompetence', verbose_name=_("Subkompetenzen"), blank=True)
    json_data = JSONField(default=dict)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=settings.SITE_ID)

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

    @classmethod
    def review_fields(cls):
        fields = {'name', 'image', 'teaser', 'learning_goals', 'related_content', 'additional_info', 'competences',
                  'sub_competences', 'tags'}
        return fields

    @property
    def help_text(self):
        content_type = ContentType.objects.get_for_model(self)
        if not hasattr(content_type, 'help_text'):
            HelpText.objects.create(content_type=content_type)
        return content_type.help_text.data()

    def submit_for_review(self, by_user: DllUser=None):
        # todo: do not allow resubmission if review is already submitted
        if self.review:
            # content was declined and now resubmitted
            review = self.review
            review.status = Review.IN_PROGRESS
            review.submitted_by = by_user
            review.save()
        else:
            Review.objects.create(content=self, is_active=True, submitted_by=by_user)
        self.send_content_submitted_mail(by_user=by_user)

    def copy_relations(self, draft_instance, public_instance):
        # image
        super(Content, self).copy_relations(draft_instance, public_instance)
        if draft_instance.image:
            public_image = draft_instance.image
            public_image.pk = None
            public_image.id = None
            file_name, extension = os.path.splitext(public_image.label)
            file_name += " (public)"
            public_image.name = file_name + extension
            public_image.save()
            public_instance.image = public_image
            public_instance.save()

        # co-authors
        public_instance.co_authors.add(*draft_instance.co_authors.all())

        # related content
        public_related_content = Content.objects.published().filter(
            publisher_draft__in=draft_instance.related_content.all())
        public_instance.related_content.add(*public_related_content)

        # competences
        public_instance.competences.add(*draft_instance.competences.all())
        public_instance.sub_competences.add(*draft_instance.sub_competences.all())

        # tags
        public_instance.tags.add(*draft_instance.tags.all())

        # links and files
        for link in draft_instance.contentlink_set.all():
            link.pk, link.id, link.created, link.modified = None, None, None, None
            link.content = public_instance
            link.save()

        for file in draft_instance.contentfile_set.all():
            # create a copy of the filer file object
            public_file = file.file
            public_file.pk, public_file.id = None, None
            file_name, extension = os.path.splitext(public_file.label)
            file_name += " (public)"
            public_file.name = file_name + extension
            public_file.save()

            # create a new instance of the ContentFile object
            file.pk, file.id, file.created, file.modified = None, None, None, None
            file.file = public_file
            file.content = public_instance
            file.save()

    def suggest_related_content(self):
        """Suggested related content based on Solr results"""
        return self.objects.none()

    def update_or_add_image_from_path(self, path, update=False, image_name=None):
        base = self.base_folder or custom_slugify(self.name)
        if self.image:
            self.image.delete()
        base_folder, created = Folder.objects.get_or_create(name=self.__class__._meta.verbose_name_plural, level=0)
        sub_folder, created = Folder.objects.get_or_create(name=base, level=1, parent=base_folder)
        images_folder, created = Folder.objects.get_or_create(name="Images", parent=sub_folder, level=2)
        if image_name is None:
            image_name = str(os.path.dirname(path).split(os.sep)[-1]) + str(os.path.splitext(path))
        file = File(open(path, 'rb'), name=image_name)
        filer_image = Image.objects.create(original_filename=image_name,
                                           file=file,
                                           folder=images_folder,
                                           owner=get_default_tuhh_user())
        self.image = filer_image
        self.save()

    def add_file_from_path(self, path, file_name=None):
        base = self.base_folder or custom_slugify(self.name)
        file = File(open(path, 'rb'), name=file_name)
        base_folder, created = Folder.objects.get_or_create(name=self.__class__._meta.verbose_name_plural, level=0)
        sub_folder, created = Folder.objects.get_or_create(name=base, level=1, parent=base_folder)
        files_folder, created = Folder.objects.get_or_create(name="Files", parent=sub_folder, level=2)
        if file_name is None:
            file_name = os.path.basename(path)
        filer_file = FilerFile.objects.create(original_filename=file_name,
                                              file=file,
                                              folder=files_folder,
                                              owner=get_default_tuhh_user())
        ContentFile.objects.create(
            file=filer_file,
            title=file_name,
            content=self
        )

    def send_content_submitted_mail(self, by_user=None):
        from dll.communication.tasks import send_mail
        relative_url = self.get_absolute_url()  # todo: set correct url to content review
        url = 'https://%s%s' % (Site.objects.get_current().domain, relative_url)
        context = {
            'link_to_content': url
        }
        if isinstance(self, TeachingModule):
            group = get_bsb_reviewer_group()
            bsb_reviewers = DllUser.objects.filter(groups__pk=group.pk)
            send_mail.delay(
                event_type_code='CONTENT_SUBMITTED_FOR_REVIEW',
                ctx=context,
                sender_id=getattr(by_user, 'pk', None),
                recipient_ids=list(bsb_reviewers.values_list('pk', flat=True))
            )
        elif isinstance(self, Trend) or isinstance(self, Tool):
            group = get_tuhh_reviewer_group()
            tuhh_reviewers = DllUser.objects.filter(groups__pk=group.pk)
            send_mail.delay(
                event_type_code='CONTENT_SUBMITTED_FOR_REVIEW',
                ctx=context,
                sender_id=getattr(by_user, 'pk', None),
                recipient_ids=list(tuhh_reviewers.values_list('pk', flat=True))
            )

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

    class Meta(RulesModelBaseMixin, PublisherModel.Meta):
        ordering = ['slug']
        verbose_name = _("Inhalt")
        verbose_name_plural = _("Inhalte")


class TeachingModule(Content):
    description = models.TextField(_("Beschreibung"), null=True, blank=True)
    subject_of_tuition = ArrayField(models.CharField(max_length=200), verbose_name=_("Unterichtsgegenstand"),
                                    default=list, null=True, blank=True)
    educational_plan_reference = models.TextField(_("Bildungsplanbezug"), null=True, blank=True)
    school_class = IntegerRangeField(verbose_name=_("Jahrgangsstufe"), null=True, blank=True)
    # estimated time e.g. Doppelstunde,unterrichtsbegleitend
    estimated_time = ArrayField(models.CharField(max_length=200), verbose_name=_("Zeitumfang"), default=list, null=True,
                                blank=True)
    equipment = ArrayField(models.CharField(max_length=200), verbose_name=_("Ausstattung"), default=list, null=True,
                           blank=True)
    state = models.CharField(_("Bundesland"), max_length=22, choices=GERMAN_STATES, null=True, blank=True)
    differentiating_attribute = models.TextField(_("Differenzierung"), max_length=500, null=True, blank=True)
    expertise = ArrayField(models.CharField(max_length=200), verbose_name=_("Fachkompetenzen"), default=list, null=True,
                           blank=True)
    subjects = models.ManyToManyField('Subject', verbose_name=_("Unterrichtsfach"), blank=True)
    school_types = models.ManyToManyField('SchoolType', verbose_name=_("Schulform"), blank=True)
    licence = models.IntegerField(_("Lizenz"), choices=LICENCE_CHOICES, blank=True, null=True)

    class Meta(Content.Meta):
        verbose_name = _("Unterrichtsbaustein")
        verbose_name_plural = _("Unterrichtsbausteine")

    @property
    def type(self):
        return 'teaching-module'

    @property
    def type_verbose(self):
        return 'Unterrichtsbaustein'

    @classmethod
    def review_fields(cls):
        fields = super().review_fields()
        fields += {'description', 'subject_of_tuition', 'educational_plan_reference', 'school_class', 'estimated_time',
                   'equipment', 'state', 'differentiating_attribute', 'expertise', 'subjects', 'subjects',
                   'school_types', 'licence'}
        return fields

    def copy_relations(self, draft_instance, public_instance):
        super(TeachingModule, self).copy_relations(draft_instance, public_instance)
        public_instance.subjects.add(*draft_instance.subjects.all())
        public_instance.school_types.add(*draft_instance.school_types.all())

    def get_absolute_url(self):
        return reverse('teaching-module-detail', kwargs={'slug': self.slug})

    def get_preview_url(self):
        return reverse('teaching-module-detail-preview', kwargs={'slug': self.slug})

    def get_edit_url(self):
        return reverse('edit-teaching-module', kwargs={'slug': self.slug})

    def get_review_url(self):
        return reverse('review-teaching-module', kwargs={'slug': self.slug})


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

    operating_systems = models.ManyToManyField('OperatingSystem', verbose_name=_("Betriebssystem"), blank=True)
    applications = models.ManyToManyField('ToolApplication', verbose_name=_("Anwendung"), blank=True)
    status = models.CharField(_("Status"), max_length=7, choices=STATUS_CHOICES, default=None, null=True)
    requires_registration = models.BooleanField(null=True, blank=False)
    usk = models.CharField(_("Altersfreigabe"), max_length=5, choices=USK_CHOICES, null=True, blank=True)
    pro = ArrayField(models.CharField(max_length=200), verbose_name=_("Pro"), default=list, null=True, blank=True)
    contra = ArrayField(models.CharField(max_length=200), verbose_name=_("Kontra"), default=list, null=True, blank=True)
    privacy = models.IntegerField(_("Datenschutz"), choices=PRIVACY_CHOICES, null=True, blank=True)
    description = models.TextField(_("Beschreibung"), null=True, blank=True)
    usage = models.TextField(_("Nutzung"), null=True, blank=True)

    class Meta(Content.Meta):
        verbose_name = _("Tool")
        verbose_name_plural = _("Tools")

    @property
    def type_verbose(self):
        return 'Tool'

    @property
    def type(self):
        return 'tool'

    @classmethod
    def review_fields(cls):
        fields = super().review_fields()
        fields += {'operating_systems', 'applications', 'status', 'requires_registration', 'usk', 'pro', 'contra',
                   'privacy', 'description', 'usage'}
        return fields

    def get_absolute_url(self):
        return reverse('tool-detail', kwargs={'slug': self.slug})

    def get_preview_url(self):
        return reverse('tool-detail-preview', kwargs={'slug': self.slug})

    def get_edit_url(self):
        return reverse('edit-tool', kwargs={'slug': self.slug})

    def get_review_url(self):
        return reverse('review-tool', kwargs={'slug': self.slug})

    def copy_relations(self, draft_instance, public_instance):
        super(Tool, self).copy_relations(draft_instance, public_instance)
        public_instance.operating_systems.add(*draft_instance.operating_systems.all())
        public_instance.applications.add(*draft_instance.applications.all())

        url_clone = draft_instance.url
        url_clone.pk = None
        url_clone.id = None
        url_clone.created = None
        url_clone.modified = None
        url_clone.tool = public_instance
        url_clone.save()


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
    target_group = ArrayField(models.CharField(max_length=200), verbose_name=_("Zielgruppe"), default=list, null=True,
                              blank=True)
    publisher = ArrayField(models.CharField(max_length=200), verbose_name=_("Herausgeber"), default=list, null=True,
                           blank=True)
    publisher_date = models.DateField(_("Datum der Veröffentlichung"), blank=True, null=True)
    central_contents = models.TextField(_("Zentrale Inhalte"), blank=True, null=True)
    citation_info = models.CharField(_("Zitierhinweis"), max_length=500, blank=True, null=True)

    class Meta(Content.Meta):
        verbose_name = _("Trend")
        verbose_name_plural = _("Trends")

    @property
    def type(self):
        return 'trend'

    @property
    def type_verbose(self):
        return 'Trend'

    @classmethod
    def review_fields(cls):
        fields = super().review_fields()
        fields += {'language', 'licence', 'category', 'target_group', 'publisher', 'publisher_date', 'central_contents',
                   'citation_info'}
        return fields

    def get_absolute_url(self):
        return reverse('trend-detail', kwargs={'slug': self.slug})

    def get_preview_url(self):
        return reverse('trend-detail-preview', kwargs={'slug': self.slug})

    def get_edit_url(self):
        return reverse('edit-trend', kwargs={'slug': self.slug})

    def get_review_url(self):
        return reverse('review-trend', kwargs={'slug': self.slug})

    def copy_relations(self, draft_instance, public_instance):
        super(Trend, self).copy_relations(draft_instance, public_instance)


class HelpText(TimeStampedModel):
    content_type = models.OneToOneField(ContentType, on_delete=models.CASCADE, related_name='help_text')

    def data(self):
        fields = self.get_fields()
        data = {}
        for field in fields:
            try:
                help_text = self.help_text_fields.get(name=str(field.name)).text
            except HelpTextField.DoesNotExist:
                help_text = getattr(field, 'help_text', None)
            data[str(field.name)] = help_text
        return data

    def get_help_text_fields_for_content_type(self):
        """
        returns the available choices for the inline admin
        :return: (('teaser', 'Teaser'), )
        """
        fields = self.get_fields()
        choices = ((str(field), str(getattr(field, 'verbose_name', field.name))) for field in fields)
        return choices

    def get_fields(self):
        model = self.content_type.model_class()
        fields = model._meta.get_fields()
        return fields

    def save(self, **kwargs):
        return super(HelpText, self).save(**kwargs)

    def __str__(self):
        return _("Hilfetext für ") + self.content_type.model_class()._meta.verbose_name_plural.title()


class HelpTextField(TimeStampedModel):
    name = models.CharField(max_length=100)
    help_text = models.ForeignKey(HelpText, on_delete=models.CASCADE, related_name='help_text_fields')
    text = models.TextField()

    class Meta:
        unique_together = ['name', 'help_text']

    def __str__(self):
        return _("Hilfetext für") + self.name


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
    count = models.PositiveSmallIntegerField(default=0)
    submitted_by = models.ForeignKey(
        DllUser, on_delete=models.SET(get_default_tuhh_user),
        related_name='submitted_reviews',
        null=True
    )
    accepted_by = models.ForeignKey(
        DllUser, on_delete=models.SET(get_default_tuhh_user),
        related_name='accepted_reviews',
        null=True
    )
    declined_by = models.ForeignKey(
        DllUser,
        on_delete=models.SET(get_default_tuhh_user),
        related_name='declined_reviews',
        null=True
    )

    def get_review_fields_for_content(self):
        return self.content.review_fields

    def save(self, **kwargs):
        if not self.pk:
            self.count = self.content.reviews.count() + 1
        return super().save(**kwargs)

    def accept(self, by_user: DllUser):
        """
        Accept the content and publish it.
        """
        if by_user.has_perm('content.change_review', self):
            self.status = self.ACCEPTED
            self.is_active = False
            self.accepted_by = by_user
            self.save()
            self.content.publish()
            self.send_review_accepted_mail()

    def decline(self, by_user: DllUser):
        if by_user.has_perm('content.change_review', self):
            self.declined_by = by_user
            self.status = self.DECLINED
            self.save()
            self.send_review_declined_mail()

    def send_review_accepted_mail(self):
        from dll.communication.tasks import send_mail
        relative_url = self.content.get_absolute_url()  # todo: set correct url to content review
        url = 'https://%s%s' % (Site.objects.get_current().domain, relative_url)
        context = {
            'link_to_content': url
        }
        cc_ids = (self.content.author.pk,) + tuple(self.content.co_authors.all().values_list('pk', flat=True))
        cc_ids = set(cc_ids) - {self.submitted_by.pk}

        send_mail.delay(
            event_type_code='REVIEW_ACCEPTED',
            ctx=context,
            sender_id=getattr(self.accepted_by, 'pk', None),
            recipient_ids=[self.submitted_by.pk],
            cc=list(cc_ids)
        )

    def send_review_declined_mail(self):
        from dll.communication.tasks import send_mail
        relative_url = self.content.get_absolute_url()  # todo: set correct url to content review
        url = 'https://%s%s' % (Site.objects.get_current().domain, relative_url)
        context = {
            'link_to_content': url
        }
        cc_ids = (self.content.author.pk,) + tuple(self.content.co_authors.all().values_list('pk', flat=True))
        cc_ids = set(cc_ids) - {self.submitted_by.pk}

        send_mail.delay(
            event_type_code='REVIEW_DECLINED',
            ctx=context,
            sender_id=getattr(self.declined_by, 'pk', None),
            recipient_ids=[self.submitted_by.pk],
            cc=list(cc_ids)
        )


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


class ToolLink(TimeStampedModel):
    url = models.URLField(max_length=2083)
    name = models.CharField(max_length=300)
    tool = models.OneToOneField('Tool', on_delete=models.CASCADE, related_name='url')


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


@receiver(models.signals.post_delete, sender=ContentFile)
def auto_delete_filer_file_on_delete(sender, instance, **kwargs):
    instance.file.delete()
