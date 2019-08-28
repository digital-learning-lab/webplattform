# -*- coding: utf-8 -*-
from django.core.management import BaseCommand

from dll.communication.models import CommunicationEventType

COMMUNICATION_EVENT_TYPES = (
    ('COAUTHOR_INVITATION', 'Co-Autor_in Einladung'),
    ('COAUTHOR_INVITATION_ACCEPTED', 'Co-Autor_in Einladung angenommen'),
    ('COAUTHOR_INVITATION_DECLINED', 'Co-Autor_in Einladung abgelehnt'),
    ('CONTACT_BSB', 'Kontakt BSB'),
    ('CONTACT_DLL', 'Kontakt TUHH'),
    ('CONTENT_SUBMITTED_FOR_REVIEW', 'Inhalt zur Prüfung eingereicht'),
    ('NEWSLETTER_CONFIRM', 'Newsletter Bestätigung'),
    ('NEWSLETTER_UNREGISTER_CONFIRM', 'Newsletter Abmeldung Bestätigung'),
    ('REVIEW_ACCEPTED', 'Inhalt freigegeben'),
    ('REVIEW_DECLINED', 'Inhalt abgelehnt'),
    ('USER_SIGNUP', 'Nutzer registriert'),
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        for event_type in COMMUNICATION_EVENT_TYPES:
            CommunicationEventType.objects.get_or_create(**{
                'code': event_type[0],
                'name': event_type[1]
            })
