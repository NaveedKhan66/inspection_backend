from django_filters import rest_framework as filters
from django.db.models import Count, Q
from users.models import User


class TradeFilter(filters.FilterSet):
    search = filters.CharFilter(method="search_filter", label="Search")
    sort_by = filters.ChoiceFilter(
        choices=[
            ("first_name", "First Name"),
            ("incomplete_items", "Incomplete Items"),
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
        model = User
        fields = ["search", "sort_by", "sort_order"]

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) | Q(last_name__icontains=value)
        )

    def filter_sort(self, queryset, name, value):
        sort_by = self.data.get("sort_by", "first_name")
        sort_order = self.data.get("sort_order", "desc")

        if sort_by == "first_name":
            # Sort by concatenated first_name and last_name
            queryset = queryset.order_by(
                f"{'-' if sort_order == 'desc' else ''}first_name",
                f"{'-' if sort_order == 'desc' else ''}last_name",
            )
        else:  # incomplete_items
            # Get the builder user for filtering incomplete items
            user = self.request.user
            if user.user_type == "employee":
                user = user.employee.builder.user

            # Annotate with incomplete items count
            incomplete_statuses = ["incomplete", "pending_approval"]
            queryset = queryset.annotate(
                incomplete_count=Count(
                    "deficiencies",
                    filter=Q(
                        deficiencies__status__in=incomplete_statuses,
                        deficiencies__home_inspection__inspection__builder=user,
                    ),
                )
            ).order_by(f"{'-' if sort_order == 'desc' else ''}incomplete_count")

        return queryset
