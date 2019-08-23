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

    def dispatch_direct_messages(self, email_address, messages, event_type=None, sender=None, cc=None):
        """
        Dispatch one-off messages to explicitly specified recipient.
        """
        if messages['subject'] and messages['body']:
            email = self.send_email_messages(email_address, messages, cc)
            if email and event_type:
                self.create_communicaton_event(event_type, email_address=email_address, sender=sender)

    def dispatch_user_messages(self, recipient, messages, event_type=None, sender=None, cc=None):
        """
        Send messages to a site user
        """
        if messages['subject'] and (messages['body'] or messages['html']):
            self.send_user_email_messages(recipient, messages, event_type, sender=sender, cc=cc)

    # Internal

    def send_user_email_messages(self, recipient, messages, event_type, sender=None, cc=None):
        """
        Sends message to the registered user / customer and collects data in database
        """
        try:
            # first choice: email of OfaUser profile
            email_address = recipient.profile.address.email
        except AttributeError:
            # fallback: email of OfaUser directly
            email_address = recipient.email
        if not email_address:
            self.logger.warning("Unable to send email messages as user #{} has no email address".format(recipient.id))
            return

        email = self.send_email_messages(email_address, messages, cc)

        if email and event_type:
            self.create_communicaton_event(event_type, email_address=email_address, recipient=recipient, sender=sender)

    def send_email_messages(self, email_address, messages, cc):
        """
        Plain email sending to the specified recipient
        """
        from_email = None

        # Determine whether we are sending a HTML version too
        if messages['html']:
            email = EmailMultiAlternatives(messages['subject'],
                                           messages['body'],
                                           from_email=from_email,
                                           to=[email_address],
                                           cc=cc)
            email.attach_alternative(messages['html'], "text/html")
        else:
            email = EmailMessage(messages['subject'],
                                 messages['body'],
                                 from_email=from_email,
                                 to=[email_address],
                                 cc=cc)
        self.logger.info("Sending email to {}".format(u(email_address)))
        email.send()

        return email

    def send_text_message(self, user, event_type):
        raise NotImplementedError

    def create_communicaton_event(self, event_type, email_address='', recipient=None, sender=None):
        CommunicationEvent.objects.create(
            event_type=event_type,
            recipient=recipient,
            sender=sender,
            email=email_address,
        )
