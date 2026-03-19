from django.urls import path

from restaurants.views import ContactsTemplateView

app_name = "restaurants"

urlpatterns = [
    path("contacts/", ContactsTemplateView.as_view(), name="contacts"),
]
