# -*- coding: utf-8 -*-
import inspect

from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import ValidationError
from rest_framework.fields import Field


class RangeField(Field):
    initial = {}
    default_error_messages = {
        "not_a_dict": _('Expected a dictionary of items but got type "{input_type}".'),
        "unexpected_keys": _('Got unexpected keys "{unexpected}".'),
        "invalid_bounds": _(
            'Bounds flags "{bounds}" not valid. Valid bounds are "{valid_bounds}".'
        ),
        "empty": _("Range may not be empty."),
    }

    valid_bounds = ("[)", "(]", "()", "[]")

    def __init__(self, range_type, **kwargs):
        self.child = kwargs.pop("child")
        self.range_type = range_type
        self.allow_empty = kwargs.pop("allow_empty", True)

        assert not inspect.isclass(self.child), "`child` has not been instantiated."
        assert self.child.source is None, (
            "The `source` argument is not meaningful when applied to a `child=` field. "
            "Remove `source=` from the field declaration."
        )

        super(RangeField, self).__init__(**kwargs)
        self.child.bind(field_name="", parent=self)

    def _valid_empty_range(self, data):
        if not data.pop("empty", False):
            return False
        if not self.allow_empty:
            self.fail("empty")
        return True

    def _validate_bounds(self, data):
        try:
            bounds = data.pop("bounds")
        except KeyError:
            return
        if bounds not in self.valid_bounds:
            self.fail(
                "invalid_bounds",
                bounds=bounds,
                valid_bounds=", ".join(self.valid_bounds),
            )
        return bounds

    def _validate_ranges(self, data):
        errors, validated_data = {}, {}
        for key in ("lower", "upper"):
            try:
                value = data.pop(key)
            except KeyError:
                continue
            else:
                try:
                    validated_data[key] = self.child.run_validation(value)
                except ValidationError as e:
                    errors[key] = e.detail

        if errors:
            raise ValidationError(errors)

        return validated_data

    def to_internal_value(self, data):
        if isinstance(data, self.range_type):
            return data

        if not isinstance(data, dict):
            self.fail("not_a_dict", input_type=type(data).__name__)

        if self._valid_empty_range(data):
            return self.range_type(empty=True)

        validated_data = self._validate_ranges(data)
        bounds = self._validate_bounds(data)
        if bounds:
            validated_data["bounds"] = bounds

        if data:
            self.fail("unexpected_keys", unexpected=", ".join(map(str, data.keys())))

        return self.range_type(**validated_data)

    def to_representation(self, value):
        if value is None:
            return value

        lower = (
            self.child.to_representation(value.lower)
            if value.lower is not None
            else None
        )
        upper = (
            self.child.to_representation(value.upper)
            if value.upper is not None
            else None
        )

        if value.isempty:
            return {"empty": True}

        return {"lower": lower, "upper": upper, "bounds": value._bounds}
