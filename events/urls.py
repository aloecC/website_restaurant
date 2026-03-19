from django.urls import path

from . import views
from .views import EventActualListView, EventListView

app_name = "events"

urlpatterns = [
    # path('contacts/', ContactsTemplateView.as_view(), name='contacts'),
    path("home/", EventActualListView.as_view(), name="events_actual_list"),
    path("events/", EventListView.as_view(), name="events_list"),
]
