# -*- coding: utf-8 -*-
from threading import local

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.flatpages.forms import FlatpageForm
from django_select2.forms import HeavySelect2Widget
from dll.content.models import HelpText, HelpTextField


_thread_locals = local()


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
        if not instance:
            self.fields['content_type'] = forms.ModelChoiceField(
                queryset=ContentType.objects.filter(model__in=['teachingmodule', 'trend', 'tool']),
                label='Art des Inhalts'
            )
        if instance:
            self.fields['content_type'] = forms.ModelChoiceField(
                queryset=ContentType.objects.filter(model__in=['teachingmodule', 'trend', 'tool']),
                widget=forms.Select(attrs={'style': 'pointer-events: none; opacity: 0.5;'}),
                initial=instance.content_type
            )


class HelpTextFieldForm(forms.ModelForm):
    name = forms.CharField(widget=HeavySelect2Widget(
        data_view='admin-help-text-choices',
        dependent_fields={'content_type': 'content_type'},
        attrs={
            'data-minimum-input-length': -1,
            'style': 'min-width: 300px'
        }
    ))

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            kwargs['initial'] = {'name': instance.name}
        super(HelpTextFieldForm, self).__init__(*args, **kwargs)
        if instance:
            self.fields['name'].widget.choices = instance.help_text.get_help_text_fields_for_content_type()


    def is_valid(self):
        return super(HelpTextFieldForm, self).is_valid()

    class Meta:
        model = HelpTextField
        fields = ['name', 'text']
