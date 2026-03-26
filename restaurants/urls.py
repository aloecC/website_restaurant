from django.urls import path

from restaurants.views import AboutUsView, ContactsTemplateView, ShowMenuView

app_name = "restaurants"

urlpatterns = [
    path("contacts/", ContactsTemplateView.as_view(), name="contacts"),
    path("about/", AboutUsView.as_view(), name="about_us"),
    path("menu/", ShowMenuView.as_view(), name="menu"),
]
