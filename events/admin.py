from django.contrib import admin

from .models import AgeGroup, Events


@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    filter_horizontal = ("recomend_audit_age",)


admin.site.register(AgeGroup)
