from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import RadioSelect

from .models import DllUser


class EditUserForm(forms.ModelForm):
    class Meta:
        model = DllUser
        fields = ['email']


class SignUpForm(UserCreationForm):
    terms_accepted = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'email',
            'first_name',
            'last_name',
            'password1'
            'password2',
            'terms_accepted'
        )
        self.fields['gender'].choices = self.fields['gender'].choices[1:]

    class Meta:
        model = DllUser
        fields = (
            'gender',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'terms_accepted'
        )
        widgets = {
            'gender': RadioSelect
        }
        labels = {
            'gender': 'Geschlecht'
        }
