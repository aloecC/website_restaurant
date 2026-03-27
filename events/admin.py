from django.contrib import admin

from .models import AgeGroup, Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (id, "name", "date_start", "min_age", "poster", "min_age")
    list_filter = ("date_start",)
    search_fields = (
        "name",
        "description",
    )

    filter_horizontal = ("recommend_audit_age",)


admin.site.register(AgeGroup)
