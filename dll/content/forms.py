# -*- coding: utf-8 -*-
from threading import local

from ckeditor.widgets import CKEditorWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, Hidden
from crispy_forms.utils import TEMPLATE_PACK
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.flatpages.forms import FlatpageForm
from django.urls import reverse
from django_select2.forms import HeavySelect2Widget
from dll.content.models import HelpText, HelpTextField, Testimonial

_thread_locals = local()


class FlatPageAdminForm(FlatpageForm):
    class Meta(FlatpageForm.Meta):
        widgets = {"content": CKEditorWidget}


class HelpTextAdminForm(forms.ModelForm):
    class Meta:
        model = HelpText
        fields = ["content_type"]

    def __init__(self, *args, **kwargs):
        super(HelpTextAdminForm, self).__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if not instance:
            self.fields["content_type"] = forms.ModelChoiceField(
                queryset=ContentType.objects.filter(
                    model__in=["teachingmodule", "trend", "tool"]
                ),
                label="Art des Inhalts",
            )
        if instance:
            self.fields["content_type"] = forms.ModelChoiceField(
                queryset=ContentType.objects.filter(
                    model__in=["teachingmodule", "trend", "tool"]
                ),
                widget=forms.Select(
                    attrs={"style": "pointer-events: none; opacity: 0.5;"}
                ),
                initial=instance.content_type,
            )


class HelpTextFieldForm(forms.ModelForm):
    name = forms.CharField(
        widget=HeavySelect2Widget(
            data_view="admin-help-text-choices",
            dependent_fields={"content_type": "content_type"},
            attrs={"data-minimum-input-length": -1, "style": "min-width: 300px"},
        )
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        if instance:
            kwargs["initial"] = {"name": instance.name}
        super(HelpTextFieldForm, self).__init__(*args, **kwargs)
        if instance:
            self.fields[
                "name"
            ].widget.choices = (
                instance.help_text.get_help_text_fields_for_content_type()
            )

    def is_valid(self):
        return super(HelpTextFieldForm, self).is_valid()

    class Meta:
        model = HelpTextField
        fields = ["name", "text"]


class CommentField(Field):
    def render(
        self,
        form,
        form_style,
        context,
        template_pack=TEMPLATE_PACK,
        extra_context=None,
        **kwargs
    ):
        if not context:
            context = {}
        context.update({"field_class": "col-lg-12"})
        return super(CommentField, self).render(
            form,
            form_style,
            context,
            template_pack=TEMPLATE_PACK,
            extra_context=None,
            **kwargs
        )


class TestimonialForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop("author")
        self.content = kwargs.get("content")
        if self.content:
            kwargs.pop("content")
        super(TestimonialForm, self).__init__(*args, **kwargs)
        self.fields["content"].initial = self.content
        self.fields["comment"].label = False
        self.helper = FormHelper()
        self.helper.form_action = reverse("testimonial")
        self.helper.form_class = "form-horizontal js-testimonialForm"
        self.helper.label_class = "col-lg-4"
        self.helper.field_class = "col-lg-8"
        if self.content:
            self.helper.layout = Layout(
                "subject",
                "school_class",
                CommentField(
                    "comment",
                    label_class="sr-only",
                    placeholder="Hier ihre Praxiserfahrung teilen...",
                ),
                Hidden("content", self.content.pk),
                Submit("submit", "Absenden", css_class="button button--primary"),
            )

    def save(self, commit=True):
        self.instance.author = self.author
        print(self.instance)
        return super(TestimonialForm, self).save(commit=commit)

    class Meta:
        model = Testimonial
        fields = ["subject", "school_class", "comment", "content"]
