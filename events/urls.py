from django.urls import path

from . import views
from .views import (
    EventActualListView,
    EventCreateView,
    EventDeleteView,
    EventDetailView,
    EventListView,
    EventUpdateView,
    ShowReservationEventDetailView,
)

app_name = "events"

urlpatterns = [
    path("home/", EventActualListView.as_view(), name="events_actual_list"),
    path("events/", EventListView.as_view(), name="events_list"),
    path("event/<int:pk>/", EventDetailView.as_view(), name="event_detail"),
    path("event/new/", EventCreateView.as_view(), name="event_create"),
    path("event/<int:pk>/edit/", EventUpdateView.as_view(), name="event_edit"),
    path("event/<int:pk>/delete/", EventDeleteView.as_view(), name="event_delete"),
    path("event/<int:pk>/reservs/", ShowReservationEventDetailView.as_view(), name="reservs_event_detail"),
]
