# -*- coding: utf-8 -*-
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.flatpages.forms import FlatpageForm
from django_select2.forms import HeavySelect2Widget
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

    def __init__(self, *args, **kwargs):
        super(HelpTextAdminForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            self.fields['content_type'] = forms.ModelChoiceField(queryset=ContentType.objects.all(), widget=forms.Select(attrs={'disabled': True}))
            pass


class HelpTextFieldForm(forms.ModelForm):
    name = forms.ChoiceField(widget=HeavySelect2Widget(data_view='admin-help-text-choices',
                                                       dependent_fields={'content_type': 'content_type'},
                                                       attrs={'data-minimum-input-length': -1,
                                                              'style': 'min-width: 300px'}))

    class Meta:
        model = HelpTextField
        fields = ['name', 'text']
