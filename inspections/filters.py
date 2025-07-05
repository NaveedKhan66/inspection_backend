import django_filters
from inspections.models import Deficiency, HomeInspection
from django.db.models import (
    Count,
    Q,
    IntegerField,
    Value,
    CharField,
    Case,
    When,
    F,
    ExpressionWrapper,
)
from django.db.models.functions import Cast, Concat, StrIndex, Left, ExtractDay, Now
from datetime import date


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
    sort_by = django_filters.ChoiceFilter(
        choices=[
            ("id", "ID"),
            ("address", "Address"),
            ("location", "Location"),
            ("status", "Status"),
            ("trade", "Trade Name"),
            ("created_date", "Created Date"),
            ("due_date", "Due Date"),
            ("outstanding_days", "Outstanding Days"),
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
            "sort_by",
            "sort_order",
        ]

    def filter_search(self, queryset, name, value):
        # Ensure the search value contains only digits
        if not value.isdigit():
            return (
                queryset.none()
            )  # Return an empty queryset if the input is not numeric

        # Convert the ID field to string for partial matching
        return queryset.filter(id__icontains=value)

    def filter_sort(self, queryset, name, value):
        sort_by = self.data.get("sort_by", "id")
        sort_order = self.data.get("sort_order", "desc")

        if sort_by == "id":
            queryset = queryset.order_by(f"{'-' if sort_order == 'desc' else ''}id")

        elif sort_by == "address":
            # Concatenate address components similar to get_home_address in serializer
            queryset = queryset.annotate(
                full_address=Concat(
                    F("home_inspection__home__street_no"),
                    Value(" "),
                    F("home_inspection__home__address"),
                    Value(" "),
                    F("home_inspection__home__city"),
                    output_field=CharField(),
                )
            ).order_by(f"{'-' if sort_order == 'desc' else ''}full_address")

        elif sort_by == "location":
            queryset = queryset.order_by(
                f"{'-' if sort_order == 'desc' else ''}location"
            )

        elif sort_by == "status":
            # Custom ordering for status
            status_order = {
                "asc": Case(
                    When(status="complete", then=Value(0)),
                    When(status="pending_approval", then=Value(1)),
                    When(status="incomplete", then=Value(2)),
                    default=Value(3),
                    output_field=IntegerField(),
                ),
                "desc": Case(
                    When(status="incomplete", then=Value(0)),
                    When(status="pending_approval", then=Value(1)),
                    When(status="complete", then=Value(2)),
                    default=Value(3),
                    output_field=IntegerField(),
                ),
            }
            queryset = queryset.annotate(
                status_order=status_order[sort_order]
            ).order_by("status_order")

        elif sort_by == "trade":
            queryset = queryset.annotate(
                trade_name=Concat(
                    F("trade__first_name"),
                    Value(" "),
                    F("trade__last_name"),
                    output_field=CharField(),
                )
            ).order_by(f"{'-' if sort_order == 'desc' else ''}trade_name")

        elif sort_by == "created_date":
            queryset = queryset.order_by(
                f"{'-' if sort_order == 'desc' else ''}created_at"
            )

        elif sort_by == "due_date":
            queryset = queryset.order_by(
                f"{'-' if sort_order == 'desc' else ''}home_inspection__due_date"
            )

        elif sort_by == "outstanding_days":
            # Calculate outstanding days similar to get_outstanding_days in serializer
            queryset = queryset.annotate(
                days_outstanding=Case(
                    When(
                        completion_date__isnull=False,
                        then=ExtractDay(
                            F("completion_date")
                            - Cast(F("created_at"), output_field=CharField())
                        ),
                    ),
                    default=ExtractDay(
                        Now() - Cast(F("created_at"), output_field=CharField())
                    ),
                    output_field=IntegerField(),
                )
            ).order_by(f"{'-' if sort_order == 'desc' else ''}days_outstanding")

        return queryset


class HomeInspectionFilter(django_filters.FilterSet):
    sort_by = django_filters.ChoiceFilter(
        choices=[
            ("total_items", "Total Items"),
            ("completed_items", "Completed Items"),
            ("pending_items", "Pending Items"),
            ("due_date", "Due Date"),
            ("lot_no", "Lot No."),
            ("address", "Address"),
            ("created_at", "Created Date"),
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
        elif sort_by == "lot_no":
            # Sort by lot_no numerically, handling formats like "01-001", "02-003", "15", "32-19"
            # Extract the number before the dash (or the whole number if no dash)
            queryset = queryset.annotate(
                lot_no_prefix=Case(
                    When(
                        home__lot_no__contains="-",
                        then=Left(
                            "home__lot_no", StrIndex("home__lot_no", Value("-")) - 1
                        ),
                    ),
                    default="home__lot_no",
                    output_field=CharField(),
                ),
                lot_no_int=Cast("lot_no_prefix", output_field=IntegerField()),
            ).order_by(f"{'-' if sort_order == 'desc' else ''}lot_no_int")
        elif sort_by == "address":
            # Sort by concatenated street_no and address
            queryset = queryset.order_by(
                f"{'-' if sort_order == 'desc' else ''}home__address"
            )
        elif sort_by == "created_at":
            # Sort by created_at date
            queryset = queryset.order_by(
                f"{'-' if sort_order == 'desc' else ''}created_at"
            )
        else:
            # Handle sorting for due_date
            queryset = queryset.order_by(
                f"{'-' if sort_order == 'desc' else ''}due_date"
            )

        return queryset
