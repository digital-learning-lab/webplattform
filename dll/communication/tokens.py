from django.contrib.auth.tokens import PasswordResetTokenGenerator


class NewsletterConfirmTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, subscription, timestamp):
        return str(subscription) + str(timestamp) + str(subscription.doi_confirmed)


class CoAuthorshipInvitationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, invitation, timestamp):
        return str(invitation) + str(timestamp) + str(invitation.accepted)


newsletter_confirm_token = NewsletterConfirmTokenGenerator()
co_author_invitation_token = CoAuthorshipInvitationTokenGenerator()
