from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class NewsletterConfirmTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, subscription, timestamp):
        return (
            six.text_type(subscription) + six.text_type(timestamp) +
            six.text_type(subscription.doi_confirmed)
        )


newsletter_confirm_token = NewsletterConfirmTokenGenerator()
