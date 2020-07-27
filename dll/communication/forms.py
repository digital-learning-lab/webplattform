from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from dll.communication.tasks import send_mail

CONTACT_OPTIONS = {
    "0": {
        "email": settings.CONTACT_EMAIL_BSB,
        "event_type_code": "CONTACT_BSB",
        "subject_verbose": _(
            "Anregungen zu den Unterrichtsbausteinen | E-Mail an die BSB"
        ),
    },
    "1": {
        "email": settings.CONTACT_EMAIL_DLL,
        "event_type_code": "CONTACT_DLL",
        "subject_verbose": _(
            "Anregungen zu Tools, Trends und zum dll allgemein | E-Mail an die TUHH"
        ),
    },
    "2": {
        "email": settings.CONTACT_EMAIL_DLL,
        "event_type_code": "CONTACT_DLL",
        "subject_verbose": _(
            "Fragen/Probleme zum Login und Einreichungsprozess | E-Mail an die TUHH"
        ),
    },
    "3": {
        "email": settings.CONTACT_EMAIL_DLL,
        "event_type_code": "CONTACT_DLL",
        "subject_verbose": _("Allgemeines Anliegen | E-Mail an die TUHH"),
    },
}


class ContactForm(forms.Form):
    from_email = forms.EmailField()
    _choices = (
        (i, CONTACT_OPTIONS[i]["subject_verbose"]) for i in CONTACT_OPTIONS.keys()
    )
    subject = forms.ChoiceField(choices=_choices)
    message = forms.CharField(max_length=700)

    def send_emails(self, user):
        context = {
            "user": getattr(user, "pk", None),
            "email": self.cleaned_data["from_email"],
            "subject": CONTACT_OPTIONS[self.cleaned_data["subject"]]["subject_verbose"],
            "message": self.cleaned_data["message"],
        }
        event_type_official = CONTACT_OPTIONS[self.cleaned_data["subject"]][
            "event_type_code"
        ]
        send_mail.delay(
            event_type_code=event_type_official,
            ctx=context,
            email=CONTACT_OPTIONS[self.cleaned_data["subject"]]["email"],
        )
        send_mail.delay(
            event_type_code="USER_CONTACT_SUCCESSFUL",
            email=self.cleaned_data["from_email"],
        )


class NewsletterForm(forms.Form):
    email_address = forms.EmailField()

    def send_registration_email(self, token):
        context = {
            "token": token,
        }
        send_mail.delay(
            event_type_code="NEWSLETTER_CONFIRM",
            ctx=context,
            email=self.cleaned_data["email_address"],
        )

    def send_unregister_email(self):
        send_mail.delay(
            event_type_code="NEWSLETTER_UNREGISTER_CONFIRM",
            email=self.cleaned_data["email_address"],
        )


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()
