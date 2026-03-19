from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls", namespace="users")),
    path("events/", include("events.urls", namespace="events")),
    path("restaurants/", include("restaurants.urls", namespace="restaurants")),
]
