from django.contrib import admin

from restaurants.models import Hall, Table


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = (id, "name", "description", "is_active", "capacity")
    list_filter = ("is_active",)
    search_fields = (
        "name",
        "description",
    )


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = (id, "number", "description", "is_active", "capacity")
    list_filter = ("is_active",)
    search_fields = ("description",)
