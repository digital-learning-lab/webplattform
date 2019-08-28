# -*- coding: utf-8 -*-
import logging

from django.utils.encoding import smart_text as u
from django.core.mail import EmailMessage, EmailMultiAlternatives

from .models import CommunicationEvent


class Dispatcher(object):
    def __init__(self, logger=None):
        if not logger:
            logger = logging.getLogger(__name__)
        self.logger = logger

    # Public API methods

    def dispatch_direct_messages(self, email_address: str, messages, event_type, sender=None, cc=None, bcc=None):
        """
        Dispatch one-off messages to explicitly specified recipient.
        """
        if messages['subject'] and messages['body']:
            email = self.send_email_messages([email_address], messages, event_type, cc, bcc)
            if email and event_type:
                self.create_communicaton_event(event_type, email_address_list=[email_address], sender=sender)

    def dispatch_user_messages(self, recipients, messages, event_type, sender=None, cc=None, bcc=None):
        """
        Send messages to a site user
        """
        if messages['subject'] and (messages['body'] or messages['html']):
            self.send_user_email_messages(recipients, messages, event_type, sender=sender, cc=cc, bcc=bcc)

    def send_user_email_messages(self, recipients, messages, event_type, sender=None, cc=None, bcc=None):
        """
        Sends message to the registered user / customer and collects data in database
        """
        email = self.send_email_messages(recipients, messages, event_type, cc=cc, bcc=bcc)

        if email and event_type:
            self.create_communicaton_event(event_type, email_address_list=recipients, cc=cc, bcc=bcc, sender=sender)

    def send_email_messages(self, recipients, messages, event_type, cc=None, bcc=None):
        """
        Plain email sending to the specified recipient
        """
        from_email = event_type.from_email
        # Determine whether we are sending a HTML version too
        if messages.get('html', None):
            email = EmailMultiAlternatives(messages['subject'],
                                           messages['body'],
                                           from_email=from_email,
                                           to=recipients,
                                           cc=cc)
            email.attach_alternative(messages['html'], "text/html")
        else:
            email = EmailMessage(messages['subject'],
                                 messages['body'],
                                 from_email=from_email,
                                 to=recipients,
                                 cc=cc)
        self.logger.info("Sending email to {}".format(', '.join(recipients)))
        email.send()

        return email

    def create_communicaton_event(self, event_type, email_address_list, cc=None, bcc=None, sender=None):
        CommunicationEvent.objects.create(
            sender=sender,
            event_type=event_type,
            from_email=event_type.from_email,
            to=email_address_list,
            cc=cc,
            bcc=bcc
        )
