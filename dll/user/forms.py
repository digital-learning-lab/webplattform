from django import forms

from user.models import DllUser


class EditUserForm(forms.ModelForm):
    class Meta:
        model = DllUser
        fields = ['email']
