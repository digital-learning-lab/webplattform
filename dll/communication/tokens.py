from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class NewsletterConfirmTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, subscription, timestamp):
        return (
            six.text_type(subscription) + six.text_type(timestamp) +
            six.text_type(subscription.doi_confirmed)
        )


class CoAuthorshipInvitationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, invitation, timestamp):
        return (
            six.text_type(invitation) + six.text_type(timestamp) +
            six.text_type(invitation.accepted)
        )


newsletter_confirm_token = NewsletterConfirmTokenGenerator()
co_author_invitation_token = CoAuthorshipInvitationTokenGenerator()
