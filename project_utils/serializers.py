from rest_framework import serializers


class SlugToIntChoiceField(serializers.ChoiceField):
    """
    Serializer to handle Extended choice fields present in models
    """

    def to_representation(self, value):
        return self.choices.get_slug_by_value(value)

    def to_internal_value(self, data):
        if data == "" and self.allow_blank:
            return ""
        try:
            return getattr(self.choices, data)
        except (KeyError, AttributeError, TypeError):
            self.fail("invalid_choice", input=data)

    def _set_choices(self, choices):
        self.grouped_choices = choices
        self._choices = choices

    def _get_choices(self):
        return self._choices

    choices = property(_get_choices, _set_choices)
