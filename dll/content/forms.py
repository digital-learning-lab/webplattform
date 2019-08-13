# -*- coding: utf-8 -*-
from ckeditor.widgets import CKEditorWidget
from django.contrib.flatpages.forms import FlatpageForm


class FlatPageAdminForm(FlatpageForm):

        class Meta(FlatpageForm.Meta):
            widgets = {
                'content':  CKEditorWidget
            }
