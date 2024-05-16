from copy import copy

from model_utils import Choices


class ExtendedChoices(Choices):
    def __init__(self, *choices):
        self.val_to_slug = {}
        self.val_to_slug_list = []

        self.slug_to_rich = {}
        self.slug_to_rich_list = []

        self.rich_to_slug = {}
        self.rich_to_slug_list = []

        super().__init__(*choices)

    def _store(self, triple, triple_collector, double_collector):
        super()._store(triple, triple_collector, double_collector)

        self.val_to_slug[triple[0]] = triple[1]
        self.val_to_slug_list.append((triple[0], triple[1]))

        self.slug_to_rich[triple[1]] = triple[2]
        self.slug_to_rich_list.append((triple[1], triple[2]))

        self.rich_to_slug[triple[2]] = triple[1]
        self.rich_to_slug_list.append((triple[2], triple[1]))

    def get_slug_by_value(self, key, default=None):
        try:
            return self.val_to_slug[key]
        except KeyError:
            return default

    def get_value_by_slug(self, slug, default=None):
        """
        Get the integer value by slug.
        """
        for val, slug_key in self.val_to_slug.items():
            if slug_key == slug:
                return val
        return default

    def get_slug_by_rich(self, key, default=None):
        try:
            return self.rich_to_slug[key]
        except KeyError:
            return default

    def slug_to_rich_only(self, include=None, exclude=None):
        if include:
            return {k: self.slug_to_rich[k] for k in include}

        if exclude:
            new_choices = copy(self.slug_to_rich)
            for k in exclude:
                if k in new_choices:
                    del new_choices[k]
            return new_choices

        return self.slug_to_rich

    def slug_to_rich_list_only(self, include=None, exclude=None):

        # TODO Temp. Add select by include
        if include:
            return self.slug_to_rich_list

        if exclude:
            return [k for k in self.slug_to_rich_list if k[0] not in exclude]

        return self.slug_to_rich_list

    def val_to_slug_list_only(self, include=None, exclude=None):

        # TODO Temp. Add select by include
        if include:
            return self.val_to_slug_list

        if exclude:
            return [k for k in self.val_to_slug_list if k[1] not in exclude]

        return self.val_to_slug_list

    def __add__(self, other):
        if isinstance(other, self.__class__):
            other = other._triples
        else:
            other = list(other)
        return ExtendedChoices(*(self._triples + other))
