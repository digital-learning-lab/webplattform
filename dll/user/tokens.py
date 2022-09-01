from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.doi_confirmed)


class EmailChangeConfirmationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, email_cr, timestamp):
        return str(email_cr.pk) + str(timestamp)


account_activation_token = AccountActivationTokenGenerator()
email_confirmation_token = EmailChangeConfirmationTokenGenerator()
