# -*- coding: utf-8 -*-
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.flatpages.forms import FlatpageForm

from dll.content.models import HelpText, HelpTextField


class FlatPageAdminForm(FlatpageForm):

        class Meta(FlatpageForm.Meta):
            widgets = {
                'content':  CKEditorWidget
            }


class HelpTextAdminForm(forms.ModelForm):

    class Meta:
        model = HelpText
        fields = ['content_type']


class HelpTextFieldForm(forms.ModelForm):

    class Meta:
        model = HelpTextField
        fields = ['name', 'text']

    def __init__(self, *args, **kwargs):
        super(HelpTextFieldForm, self).__init__(*args, **kwargs)
        # todo: make a choices select
        instance: HelpTextField = kwargs.get('instance')
        if instance:
            help_text = instance.help_text
            if help_text:
                self.fields['name'] = forms.ChoiceField(choices=help_text.get_help_text_fields_for_content_type())

