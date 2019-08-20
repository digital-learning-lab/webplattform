# -*- coding: utf-8 -*-
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.flatpages.forms import FlatpageForm

from dll.content.models import HelpText


class FlatPageAdminForm(FlatpageForm):

        class Meta(FlatpageForm.Meta):
            widgets = {
                'content':  CKEditorWidget
            }


class HelpTextAdminForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(HelpTextAdminForm, self).__init__(*args, **kwargs)
        instance: HelpText = kwargs.get('instance')
        if instance:
            for key, value in instance.json_data.items():
                self.fields[key] = forms.CharField()
