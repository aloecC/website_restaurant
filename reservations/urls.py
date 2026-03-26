from django.urls import path

from . import views
from .views import (
    ReservationCreateView,
    ReservationDeleteView,
    ReservationDetailView,
    ReservationListView,
    ReservationSuccessView,
    ReservationTableListView,
    ReservationUpdateView,
    ScoreTemplateView,
    ScoreViewTemplateView,
)

app_name = "reservations"

urlpatterns = [
    path("reservations/", ReservationListView.as_view(), name="reservation_list"),
    path("reservations/show_tables/", ReservationTableListView.as_view(), name="reservation_table_list"),
    path("reservation/new/", ReservationCreateView.as_view(), name="reservation_create"),
    path("reservation/success/", ReservationSuccessView.as_view(), name="reservation_success"),
    path("reservation/<int:pk>/", ReservationDetailView.as_view(), name="reservation_detail"),
    path("reservation/<int:pk>/edit/", ReservationUpdateView.as_view(), name="reservation_edit"),
    path("reservation/<int:pk>/delete/", ReservationDeleteView.as_view(), name="reservation_delete"),
    path("reservation/<int:pk>/score/", ScoreTemplateView.as_view(), name="reservation_score"),
    path("reservation/<int:pk>/score/show/", ScoreViewTemplateView.as_view(), name="reservation_score_show"),
]
