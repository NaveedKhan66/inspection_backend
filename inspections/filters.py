import django_filters
from inspections.models import Deficiency, HomeInspection
from django.db.models import Count, Q


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
    lot_no = django_filters.CharFilter(field_name="home_inspection__home__lot_no")
    address = django_filters.CharFilter(field_name="home_inspection__home__address")
    postal_code = django_filters.CharFilter(
        field_name="home_inspection__home__postal_code"
    )
    project_id = django_filters.UUIDFilter(
        field_name="home_inspection__home__project__id"
    )
    builder_id = django_filters.UUIDFilter(
        field_name="home_inspection__inspection__builder__id"
    )
    street_no = django_filters.CharFilter(field_name="home_inspection__home__street_no")

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
            "project_id",
            "builder_id",
            "street_no",
        ]

    def filter_search(self, queryset, name, value):
        # Ensure the search value contains only digits
        if not value.isdigit():
            return (
                queryset.none()
            )  # Return an empty queryset if the input is not numeric

        # Convert the ID field to string for partial matching
        return queryset.filter(id__icontains=value)


class HomeInspectionFilter(django_filters.FilterSet):
    sort_by = django_filters.ChoiceFilter(
        choices=[
            ("total_items", "Total Items"),
            ("completed_items", "Completed Items"),
            ("pending_items", "Pending Items"),
            ("due_date", "Due Date"),
        ],
        method="filter_sort",
    )
    sort_order = django_filters.ChoiceFilter(
        choices=[
            ("asc", "Ascending"),
            ("desc", "Descending"),
        ],
        method="filter_sort",
    )

    class Meta:
        model = HomeInspection
        fields = ["sort_by", "sort_order"]

    def filter_sort(self, queryset, name, value):
        sort_by = self.data.get("sort_by", "due_date")
        sort_order = self.data.get("sort_order", "desc")

        if sort_by in ["total_items", "completed_items", "pending_items"]:
            if sort_by == "total_items":
                queryset = queryset.annotate(
                    total_items_count=Count("deficiencies")
                ).order_by(f"{'-' if sort_order == 'desc' else ''}total_items_count")
            elif sort_by == "completed_items":
                queryset = queryset.annotate(
                    completed_items_count=Count(
                        "deficiencies", filter=Q(deficiencies__status="complete")
                    )
                ).order_by(
                    f"{'-' if sort_order == 'desc' else ''}completed_items_count"
                )
            elif sort_by == "pending_items":
                queryset = queryset.annotate(
                    pending_items_count=Count(
                        "deficiencies",
                        filter=Q(
                            deficiencies__status__in=["incomplete", "pending_approval"]
                        ),
                    )
                ).order_by(f"{'-' if sort_order == 'desc' else ''}pending_items_count")
        else:
            # Handle sorting for due_date
            queryset = queryset.order_by(
                f"{'-' if sort_order == 'desc' else ''}due_date"
            )

        return queryset
