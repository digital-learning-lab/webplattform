import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, ButtonHolder, Fieldset

from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordChangeForm,
    PasswordResetForm,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from wagtail.core.templatetags.wagtailcore_tags import slugurl

from .models import DllUser

from ..communication.tasks import send_mail


class EditUserForm(forms.ModelForm):
    class Meta:
        model = DllUser
        fields = ["email"]


class SignUpForm(UserCreationForm):
    terms_accepted = forms.BooleanField(required=True)
    newsletter_registration = forms.BooleanField(
        label="Ja, ich möchte den Newsletter des digital.learning.labs erhalten.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        data_privacy_url = kwargs.pop("privacy_url")
        terms = kwargs.pop("terms")
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit("submit", "Absenden", css_class="button button--primary")
        )
        self.fields["terms_accepted"].label = (
            f'Ja, ich stimme den <a href="{terms}">Nutzungsbedingungen</a>- und den '
            f'<a href="{data_privacy_url}">Datenschutzbestimmungen</a> des digital.learning.lab zu.'
        )
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True

    def send_registration_email(self, token):
        context = {
            "token": token,
        }
        send_mail.delay(
            event_type_code="NEWSLETTER_CONFIRM",
            ctx=context,
            email=self.cleaned_data["email"],
        )

    class Meta:
        model = DllUser
        fields = (
            "first_name",
            "last_name",
            "email",
            "newsletter_registration",
            "terms_accepted",
            "password1",
            "password2",
        )
        labels = {"terms_accepted": "Nutzungs- und Datenschutzbestimmungen"}


class UserProfileForm(forms.ModelForm):
    """
    This form is just used for displaying the profile info
    """

    full_name = forms.CharField(disabled=True, required=False, label=_("Name"))
    email = forms.CharField(disabled=True, required=False, label=_("E-Mail"))
    status = forms.CharField(disabled=True, required=False, label=_("Status"))
    joined = forms.CharField(disabled=True, required=False, label=_("Beigetreten"))

    class Meta:
        model = DllUser
        fields = ("full_name", "email", "joined", "status")

    def __init__(self, **kwargs):
        super(UserProfileForm, self).__init__(**kwargs)
        self.fields["full_name"].initial = self.instance.full_name
        self.fields["status"].initial = ", ".join(map(str, self.instance.status_list))
        if isinstance(self.instance.doi_confirmed_date, datetime.datetime):
            self.fields["joined"].initial = self.instance.doi_confirmed_date.strftime(
                "%d %B %Y"
            )

    def save(self, commit=True):
        # do not save any changes here
        pass


class UserEmailsForm(forms.ModelForm):
    class Meta:
        model = DllUser
        fields = ("email",)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if self.has_changed() and DllUser.objects.filter(email=email).exists():
            raise ValidationError(
                _("Es existiert bereits ein Konto mit dieser E-Mail Adresse.")
            )
        return email

    def save(self, commit=True):
        # do not save any changes here
        pass


class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, **kwargs):
        self.instance = kwargs.pop("instance")
        super(UserPasswordChangeForm, self).__init__(self.instance, **kwargs)

    def clean_new_password2(self):
        password2 = super(UserPasswordChangeForm, self).clean_new_password2()
        if password2 == self.cleaned_data.get("old_password"):
            raise forms.ValidationError(
                _(
                    "Old and new password must be different. Please use another new password."
                ),
                code="password_not_changed",
            )
        return password2


class UserAccountDeleteForm(forms.Form):
    conditions = forms.BooleanField(
        widget=forms.CheckboxInput,
        label=_(
            "Ich bestätige, dass ich weiterhin namentlich in meinen erstellten und bearbeiteten Inhalten gelistet "
            "werde."
        ),
        required=False,
    )

    def __init__(self, **kwargs):
        self.instance = kwargs.pop("instance")
        super(UserAccountDeleteForm, self).__init__(**kwargs)
        self.helper = FormHelper()
        submit_button = Submit("submit", "Löschen")
        submit_button.field_classes = "button button--danger"
        self.helper.layout = Layout(
            Fieldset(
                "",
                "conditions",
            ),
            ButtonHolder(submit_button),
        )

    def clean_conditions(self):
        if not self.cleaned_data["conditions"]:
            raise forms.ValidationError(
                "Bitte bestätigen Sie den Bestand Ihrer erstellen und bearbeiteten Inhalte oder wenden Sie sich über "
                "das Kontaktformular direkt an uns.",
                code="keep_contents_not_accepted",
            )
        return self.cleaned_data

    def save(self):
        self.instance.delete()


class DLLPasswordResetForm(PasswordResetForm):
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        context.pop("user")
        send_mail.delay(
            event_type_code="USER_PASSWORD_RESET", ctx=context, email=to_email
        )
