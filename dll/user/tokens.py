from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.doi_confirmed)
        )


class EmailChangeConfirmationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, email_cr, timestamp):
        return (
            six.text_type(email_cr.pk) + six.text_type(timestamp)
        )


account_activation_token = AccountActivationTokenGenerator()
email_confirmation_token = EmailChangeConfirmationTokenGenerator()
