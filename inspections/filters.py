import django_filters
from inspections.models import Deficiency


class DeficiencyFilter(django_filters.FilterSet):
    inspection_id = django_filters.UUIDFilter(
        field_name="home_inspection__inspection__id"
    )
    home_id = django_filters.UUIDFilter(field_name="home_inspection__home__id")
    home_inspection_id = django_filters.NumberFilter(field_name="home_inspection__id")
    location = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.ChoiceFilter(choices=Deficiency.STATUS_TYPES)
    trade = django_filters.UUIDFilter(field_name="trade__id")
    search = django_filters.CharFilter(method="filter_search")
    lot_no = django_filters.UUIDFilter(field_name="home_inspection__home__lot_no")
    address = django_filters.UUIDFilter(field_name="home_inspection__home__address")
    postal_code = django_filters.UUIDFilter(
        field_name="home_inspection__home__postal_code"
    )

    class Meta:
        model = Deficiency
        fields = [
            "inspection_id",
            "home_id",
            "home_inspection_id",
            "location",
            "status",
            "trade",
            "search",
            "lot_no",
            "address",
            "postal_code",
        ]

    def filter_search(self, queryset, name, value):
        # Ensure the search value contains only digits
        if not value.isdigit():
            return (
                queryset.none()
            )  # Return an empty queryset if the input is not numeric

        # Convert the ID field to string for partial matching
        return queryset.filter(id__icontains=value)
