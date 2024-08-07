import django_filters
from inspections.models import Deficiency


class DeficiencyFilter(django_filters.FilterSet):
    inspection_id = django_filters.UUIDFilter(
        field_name="home_inspection__inspection__id"
    )
    home_id = django_filters.UUIDFilter(field_name="home_inspection__home__id")

    class Meta:
        model = Deficiency
        fields = ["inspection_id", "home_id", "status"]
