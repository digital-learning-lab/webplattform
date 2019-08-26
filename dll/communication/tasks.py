import logging

from dll.communication.models import CommunicationEventType
from dll.communication.utils import Dispatcher
from dll.user.models import DllUser

logger = logging.getLogger('dll.communication.tasks')


def send_mail(event_type_code, ctx={}, recipient_ids=None, sender_id=None, email=None, cc=None, bcc=None):
    _retry = 1  # self.request.retries
    logger.debug('Email sending initiated - attempt nr. {}'.format(_retry))
    if not (recipient_ids or email):
        raise ValueError('You must provide either a recipient or an email')

    dispatcher = Dispatcher()

    event_type = CommunicationEventType.objects.get(code=event_type_code)

    sender = DllUser.objects.get(pk=sender_id) if sender_id else None

    messages = event_type.get_messages(ctx=ctx)

    try:
        logger.debug('Sending email')
        if email:  # send directly to provided email addresses
            dispatcher.dispatch_direct_messages(
                sender=sender,
                event_type=event_type,
                email_address=email,
                messages=messages,
                cc=cc,
                bcc=bcc
            )
        else:
            recipients = list(DllUser.objects.filter(pk__in=recipient_ids).values_list('email', flat=True))
            dispatcher.dispatch_user_messages(
                sender=sender,
                event_type=event_type,
                recipients=recipients,
                messages=messages,
                cc=cc,
                bcc=bcc
            )
    except Exception as e:
        logger.warning('Sending email failed. Event type code: {}'.format(event_type_code))
        logger.exception(e)


# todo: remove too old unconfirmed subscriptions periodically.
# But emails will still be saved because CommunicationEvents were created... What to do about that?
