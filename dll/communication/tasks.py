import logging

from dll.communication.models import CommunicationEventType
from dll.communication.utils import Dispatcher
from dll.user.models import DllUser

logger = logging.getLogger('dll.communication.tasks')


def send_mail(event_type_code, ctx={}, recipient_id=None, sender_id=None, email=None, cc=None):
    _retry = 1  # self.request.retries
    logger.debug('Email sending initiated - attempt nr. {}'.format(_retry))
    if not (recipient_id or email):
        raise ValueError('You must provide either a recipient or an email')

    dispatcher = Dispatcher()

    event_type = CommunicationEventType.objects.get(code=event_type_code)

    sender = DllUser.objects.get(pk=sender_id) if sender_id else None

    messages = event_type.get_messages(ctx=ctx)

    try:
        logger.debug('Sending email')
        if email:  # send directly to provided email address
            dispatcher.dispatch_direct_messages(
                email_address=email,
                messages=messages,
                event_type=event_type,
                sender=sender,
                cc=cc
            )
        else:
            recipient = DllUser.objects.get(pk=recipient_id)
            dispatcher.dispatch_user_messages(
                recipient=recipient,
                messages=messages,
                event_type=event_type,
                sender=sender,
                cc=cc
            )
    except Exception as e:
        logger.warning('Sending email failed. Event type code: {}'.format(event_type_code))
        logger.exception(e)


# todo: remove too old unconfirmed subscriptions periodically.
# But emails will still be saved because CommunicationEvents were created... What to do about that?
