from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, TemporaryUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ["email", "username", "is_staff", "gender", "age_group"]
    list_filter = ["is_staff", "is_active", "gender"]
    ordering = ["email"]
    search_fields = ["email", "username"]


admin.site.register(CustomUser, CustomUserAdmin)
