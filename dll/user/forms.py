import datetime

from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, PasswordChangeForm
from django.urls import reverse_lazy

from .models import DllUser
from django.utils.translation import ugettext_lazy as _


class EditUserForm(forms.ModelForm):
    class Meta:
        model = DllUser
        fields = ['email']


class SignUpForm(UserCreationForm):
    terms_accepted = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        data_privacy_url = reverse_lazy('data-privacy')
        self.fields['terms_accepted'].label = f'Ja, ich stimme den <a href="/">Nutzungsbedingungen</a>- und den ' \
        f'<a href="{data_privacy_url}">Datenschutzbestimmungen</a> des digital.learning.lab zu.'
        # self.helper.layout = Layout(
        #     'email',
        #     'first_name',
        #     'last_name',
        #     'password1'
        #     'password2',
        #     'terms_accepted'
        # )
        # self.fields['gender'].choices = self.fields['gender'].choices[1:]

    class Meta:
        model = DllUser
        fields = (
            # 'gender',
            'first_name',
            'last_name',
            'email',
            'terms_accepted',
            'password1',
            'password2',
        )
        labels = {
            'terms_accepted': 'Nutzungs- und Datenschutzbestimmungen'
        }


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
        fields = ('full_name', 'email', 'joined', 'status')

    def __init__(self, **kwargs):
        super(UserProfileForm, self).__init__(**kwargs)
        self.fields['full_name'].initial = self.instance.full_name
        self.fields['status'].initial = 'Reviewer' if self.instance.is_reviewer else None
        if isinstance(self.instance.doi_confirmed_date, datetime.datetime):
            self.fields['joined'].initial = self.instance.doi_confirmed_date.strftime("%d %B %Y")

    def save(self, commit=True):
        # do not save any changes here
        pass


class UserEmailsForm(forms.Form):

    def __init__(self, **kwargs):
        self.instance = kwargs.pop('instance')
        super(UserEmailsForm, self).__init__(**kwargs)
        self.fields['emails'] = forms.ChoiceField(choices=[(self.instance.email, self.instance.email)], widget=forms.RadioSelect)


class UserPasswordChangeForm(PasswordChangeForm):

    def __init__(self, **kwargs):
        self.instance = kwargs.pop('instance')
        super(UserPasswordChangeForm, self).__init__(self.instance, **kwargs)


class UserAccountDeleteForm(forms.Form):
    conditions = forms.BooleanField(widget=forms.CheckboxInput,
                                    label=_("Ich habe die Bedingungen gelesen und akzeptiere sie."))

    def __init__(self, **kwargs):
        self.instance = kwargs.pop('instance')
        super(UserAccountDeleteForm, self).__init__(**kwargs)

    def save(self):
        self.instance.delete()
