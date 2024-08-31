from django_filters import rest_framework as filters
from .models import Home
from django.db.models import Q


class HomeFilter(filters.FilterSet):
    search = filters.CharFilter(method="search_filter", label="Search")

    class Meta:
        model = Home
        fields = ["lot_no", "enrollment_no", "search"]

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(lot_no__icontains=value) | Q(enrollment_no__icontains=value)
        )
