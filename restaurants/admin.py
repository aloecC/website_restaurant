from django.contrib import admin

from restaurants.models import Table, TeamMember


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = (id, "number", "description", "is_active", "capacity")
    list_filter = ("is_active",)
    search_fields = ("description",)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = (id, "first_name", "last_name", "description", "position", "is_public")
    list_filter = ("is_public",)
    search_fields = ("description",)
