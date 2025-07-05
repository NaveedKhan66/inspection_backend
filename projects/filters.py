from django_filters import rest_framework as filters
from .models import Home
from django.db.models import Q, IntegerField, CharField, Case, When, Value
from django.db.models.functions import Cast, StrIndex, Left


class HomeFilter(filters.FilterSet):
    search = filters.CharFilter(method="search_filter", label="Search")
    sort_by = filters.ChoiceFilter(
        choices=[
            ("lot_no", "Lot No."),
            ("enrollment_no", "Enrollment No."),
            ("warranty_start_date", "Warranty Start Date"),
        ],
        method="filter_sort",
    )
    sort_order = filters.ChoiceFilter(
        choices=[
            ("asc", "Ascending"),
            ("desc", "Descending"),
        ],
        method="filter_sort",
    )

    class Meta:
        model = Home
        fields = ["lot_no", "enrollment_no", "search", "sort_by", "sort_order"]

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(lot_no__icontains=value) | Q(enrollment_no__icontains=value)
        )

    def filter_sort(self, queryset, name, value):
        sort_by = self.data.get("sort_by", "lot_no")
        sort_order = self.data.get("sort_order", "desc")

        if sort_by == "lot_no":
            # Sort by lot_no numerically, handling formats like "01-001", "02-003", "15", "32-19"
            # Extract the number before the dash (or the whole number if no dash)
            queryset = queryset.annotate(
                lot_no_prefix=Case(
                    When(
                        lot_no__contains="-",
                        then=Left("lot_no", StrIndex("lot_no", Value("-")) - 1),
                    ),
                    default="lot_no",
                    output_field=CharField(),
                ),
                lot_no_int=Cast("lot_no_prefix", output_field=IntegerField()),
            ).order_by(f"{'-' if sort_order == 'desc' else ''}lot_no_int")
        elif sort_by == "enrollment_no":
            queryset = queryset.order_by(
                f"{'-' if sort_order == 'desc' else ''}enrollment_no"
            )
        else:  # warranty_start_date
            queryset = queryset.order_by(
                f"{'-' if sort_order == 'desc' else ''}warranty_start_date"
            )

        return queryset
