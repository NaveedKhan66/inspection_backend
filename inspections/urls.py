from django.urls import path, include
from inspections.views import builder
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"inspections", builder.InspectionViewSet, basename="inspection")

deficiency_router = DefaultRouter()
deficiency_router.register(
    r"deficiencies", builder.DeficiencyViewSet, basename="deficiency"
)


urlpatterns = [
    path(r"", include(router.urls)),
    path(
        "inspection/",
        include(deficiency_router.urls),
        name="inspection-deficiency",
    ),
    path(
        "deficiency/image/<int:pk>",
        builder.DefImageDeleteView.as_view(),
        name="deficiency-image-delete",
    ),
    path(
        "builder/trade/<uuid:trade_id>/deficiencies/",
        builder.BuilderTradeDeficiencyListView.as_view(),
        name="builder-trade-deficiency-list",
    ),
    path(
        "inspection/review/",
        builder.InspectionReviewCreateView.as_view(),
        name="deficiency-review",
    ),
    path(
        "deficiency/email/",
        builder.SendDeficiencyEmailView.as_view(),
        name="deficiency-email",
    ),
    path(
        "home/<uuid:home_id>/inspections/",
        builder.HomeInspectionListView.as_view(),
        name="home-inspections-list",
    ),
    path(
        "deficiencies-overview/",
        builder.TotalDeficiencies.as_view(),
        name="total-deficiencies",
    ),
    path(
        "project-deficiencies-overview/",
        builder.ProjectTotalDeficiencies.as_view(),
        name="deficiencies-overview",
    ),
    path(
        "deficiencies-filter/",
        builder.DeficiencyFilterView.as_view(),
        name="deficiencies-filter",
    ),
    path(
        "inspection/deficiencies-filter/",
        builder.DeficiencyInspectionFilterView.as_view(),
        name="deficiencies-inspection-filter",
    ),
]
